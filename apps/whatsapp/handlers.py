from datetime import datetime

from django.db import transaction
from django.utils import timezone

from apps.appointments.services import create_appointment
from apps.conversations.models import Conversation, Message, MessageDirection
from apps.customers.services import create_customer, get_customer_by_phone
from apps.services.selectors import get_services_for_business
from apps.staff.models import Staff


class ConversationContext:
    def __init__(self, business, customer, conversation):
        self.business = business
        self.customer = customer
        self.conversation = conversation
        self.selected_service = None
        self.selected_staff = None
        self.selected_date = None
        self.selected_time = None
        ctx_data = conversation.context_data or {}
        self.selected_staff_id = ctx_data.get("staff_id")


def handle_incoming_message(business, msg):
    from .adapters import send_whatsapp_message

    phone = msg.get("from")
    content = msg.get("text", {}).get("body", "")

    customer, _ = _get_or_create_customer(business, phone)

    conversation = _get_or_create_conversation(business, customer)

    _persist_message(conversation, MessageDirection.INBOUND, content)

    ctx = ConversationContext(business, customer, conversation)

    response, new_state, context_updates = _generate_response_and_updates(
        ctx, content
    )

    if response:
        _persist_message(conversation, MessageDirection.OUTBOUND, response)
        send_whatsapp_message(business, phone, response)

    if new_state != conversation.state or context_updates:
        _update_conversation(conversation, new_state, context_updates)


def _get_or_create_customer(business, phone):
    try:
        customer = get_customer_by_phone(business, phone)
        return customer, False
    except Exception:
        return create_customer(
            business=business,
            name=phone,
            phone=phone,
        ), True


def _get_or_create_conversation(business, customer):
    from .services import ConversationState

    conversation, _ = Conversation.objects.get_or_create(
        business=business,
        customer=customer,
        defaults={"state": ConversationState.INITIAL, "context_data": {}}
    )
    return conversation


def _persist_message(conversation, direction, content):
    return Message.objects.create(
        conversation=conversation,
        direction=direction,
        content=content,
    )


def _generate_response_and_updates(ctx, content):
    from .services import ConversationState

    text = content.strip().lower()
    conversation = ctx.conversation
    state = conversation.state or ConversationState.INITIAL
    context = conversation.context_data or {}

    new_state = state
    context_updates = {}

    if state == ConversationState.INITIAL:
        if any(w in text for w in ["reserva", "turno", "cita", "hola", "buenas"]):
            services = _list_services(ctx.business)
            if not services:
                return (
                    "Hola! Lamentablemente no hay servicios disponibles en este momento.",
                    state,
                    {}
                )
            new_state = ConversationState.AWAITING_SERVICE
            return (
                "Hola! 👋 Vamos a gestionar tu turno.\n\n"
                + "¿Qué servicio necesitas?\n\n"
                + services,
                new_state,
                {}
            )
        return (
            "Hola! Escribí 'reserva' o 'turno' para comenzar con la gestión.",
            state,
            {}
        )

    if state == ConversationState.AWAITING_SERVICE:
        idx = _parse_service_selection(text, ctx.business)
        if idx is not None:
            services = list(get_services_for_business(ctx.business)[:5])
            if 0 <= idx < len(services):
                service = services[idx]
                context_updates["service_id"] = str(service.id)
                context_updates["service_name"] = service.name
                new_state = ConversationState.AWAITING_STAFF
                staff_list = _list_staff(ctx.business, service)
                if staff_list:
                    return (
                        f"Perfecto! {service.name}\n\n¿Con quién preferís?\n\n{staff_list}",
                        new_state,
                        context_updates
                    )
                return (
                    f"Perfecto! {service.name}\n\n¿Qué fecha te gustaría? (ej: 20/07)",
                    ConversationState.AWAITING_DATE,
                    context_updates
                )
        return (
            "Por favor selecciona un número de la lista de servicios.",
            state,
            {}
        )

    if state == ConversationState.AWAITING_STAFF:
        staff_id = _parse_staff_selection(text, ctx.business, context.get("service_id"))
        if staff_id:
            context_updates["staff_id"] = staff_id
            new_state = ConversationState.AWAITING_DATE
            return (
                "¿Qué fecha te gustaría? (ej: 20/07)",
                new_state,
                context_updates
            )
        return (
            "Por favor selecciona un número de la lista de personal.",
            state,
            {}
        )

    if state == ConversationState.AWAITING_DATE:
        parsed_date = _parse_date(text)
        if parsed_date:
            context_updates["date"] = parsed_date.strftime("%Y-%m-%d")
            context_updates["date_display"] = parsed_date.strftime("%d/%m/%Y")
            new_state = ConversationState.AWAITING_TIME
            return (
                f"Fecha: {parsed_date.strftime('%d/%m/%Y')}\n\n"
                "¿Qué horario te conviene? (ej: 10:00 o 14:30)",
                new_state,
                context_updates
            )
        return (
            "No entendí la fecha. Por favor usá el formato DD/MM (ej: 20/07)",
            state,
            {}
        )

    if state == ConversationState.AWAITING_TIME:
        parsed_time = _parse_time(text)
        if parsed_time:
            context_updates["time"] = parsed_time.strftime("%H:%M")
            new_state = ConversationState.AWAITING_CONFIRMATION
            date_display = context.get("date_display", "?")
            return (
                f"Fecha: {date_display}\n"
                f"Hora: {parsed_time.strftime('%H:%M')}\n\n"
                "🔔 ¿Confirmás este turno?\n\n"
                "Respodé *SI* para confirmar o *NO* para cancelar.",
                new_state,
                context_updates
            )
        return (
            "No entendí el horario. Por favor usá formato HH:MM (ej: 10:00 o 14:30)",
            state,
            {}
        )

    if state == ConversationState.AWAITING_CONFIRMATION:
        if any(w in text for w in ["si", "sí", "confirmo", "sí,confirmar"]):
            result = _create_appointment_from_context(ctx, context)
            if result["success"]:
                new_state = ConversationState.CONFIRMED
                return (
                    f"✅ ¡Turno confirmado!\n\n"
                    f"📅 {context.get('date_display', '')}\n"
                    f"🕐 {context.get('time', '')}\n"
                    f"🔧 {context.get('service_name', '')}\n\n"
                    f"Te recordaremos 24hs antes del turno.\n\n"
                    f"¿Necesitás algo más?",
                    new_state,
                    {}
                )
            else:
                return (
                    f"❌ No pudimos confirmar el turno: {result['error']}\n\n"
                    "Por favor intentá de nuevo o contacta al negocio.",
                    ConversationState.INITIAL,
                    {}
                )
        elif any(w in text for w in ["no", "cancelar", "n"]):
            new_state = ConversationState.INITIAL
            return (
                "Ok, el turno fue cancelado.\n\n"
                "¿Necesitás algo más?",
                new_state,
                {}
            )
        return (
            "Por favor respondé *SI* para confirmar o *NO* para cancelar.",
            state,
            {}
        )

    if state == ConversationState.CONFIRMED:
        if any(w in text for w in ["si", "sí", "gracias", "chau", "adiós"]):
            return (
                "¡De nada! Que tengas un excelente día. 👋",
                state,
                {}
            )
        return (
            "¡Tu turno ya está confirmado!\n\n"
            "¿Necesitás algo más?",
            state,
            {}
        )

    return (
        "Lo siento, no entendí. Escribí 'reserva' para comenzar.",
        ConversationState.INITIAL,
        {}
    )


def _list_services(business):
    services = get_services_for_business(business)
    if not services:
        return None
    lines = []
    for i, s in enumerate(services[:5], 1):
        lines.append(f"{i}. {s.name} ({s.duration_minutes} min)")
    return "\n".join(lines)


def _list_staff(business, service):
    staff_members = Staff.objects.filter(
        business=business,
        is_active=True,
        services=service
    )[:5]
    if not staff_members:
        return None
    lines = []
    for i, s in enumerate(staff_members, 1):
        name = s.user.get_full_name() or s.user.username
        lines.append(f"{i}. {name}")
    return "\n".join(lines)


def _parse_service_selection(text, business):
    try:
        idx = int(text.strip()) - 1
        services = list(get_services_for_business(business)[:5])
        if 0 <= idx < len(services):
            return idx
    except ValueError:
        pass
    return None


def _parse_staff_selection(text, business, service_id):
    try:
        idx = int(text.strip()) - 1
        staff_members = Staff.objects.filter(
            business=business,
            is_active=True
        )
        if service_id:
            staff_members = staff_members.filter(services__id=service_id)
        staff_list = list(staff_members[:5])
        if 0 <= idx < len(staff_list):
            return str(staff_list[idx].id)
    except ValueError:
        pass
    return None


def _parse_date(text):
    text = text.strip()
    for fmt in ["%d/%m", "%d/%m/%Y", "%d-%m-%Y"]:
        try:
            dt = datetime.strptime(text, fmt)
            now = timezone.now()
            if dt.year == 1900:
                dt = dt.replace(year=now.year)
            if dt.date() < now.date():
                return None
            return dt
        except ValueError:
            continue
    return None


def _parse_time(text):
    text = text.strip().replace(".", ":").replace(",", ":")
    for fmt in ["%H:%M", "%H:%M:%S"]:
        try:
            return datetime.strptime(text, fmt).time()
        except ValueError:
            continue
    return None


@transaction.atomic
def _create_appointment_from_context(ctx, context):
    from apps.appointments.models import Appointment
    from apps.services.models import Service
    from apps.staff.models import Staff

    try:
        service_id = context.get("service_id")
        staff_id = context.get("staff_id")
        date_str = context.get("date")
        time_str = context.get("time")

        if not all([service_id, date_str, time_str]):
            return {"success": False, "error": "Faltan datos del turno"}

        service = Service.objects.get(id=service_id)
        staff = Staff.objects.get(id=staff_id) if staff_id else None

        date_parts = date_str.split("-")
        time_parts = time_str.split(":")

        starts_at = datetime(
            int(date_parts[0]),
            int(date_parts[1]),
            int(date_parts[2]),
            int(time_parts[0]),
            int(time_parts[1]),
        )
        starts_at = timezone.make_aware(starts_at)

        if not staff:
            available_staff = Staff.objects.filter(
                business=ctx.business,
                is_active=True,
                services=service
            ).first()
            if not available_staff:
                return {"success": False, "error": "No hay personal disponible"}
            staff = available_staff

        existing = Appointment.objects.filter(
            staff=staff,
            starts_at=starts_at,
            status__in=["pending", "confirmed"]
        ).exists()
        if existing:
            return {"success": False, "error": "El horario no está disponible"}

        appointment = create_appointment(
            business=ctx.business,
            customer=ctx.customer,
            service=service,
            staff=staff,
            starts_at=starts_at,
        )

        return {"success": True, "appointment": appointment}

    except Exception as e:
        return {"success": False, "error": str(e)}


@transaction.atomic
def _update_conversation(conversation, new_state, context_updates):
    from .services import ConversationState, can_transition

    current_state = conversation.state or ConversationState.INITIAL

    if new_state != current_state and can_transition(current_state, new_state):
        conversation.state = new_state

    if context_updates:
        current_context = conversation.context_data or {}
        current_context.update(context_updates)
        conversation.context_data = current_context

    conversation.save()
