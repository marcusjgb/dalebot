from django.db import transaction

from apps.conversations.models import Conversation, Message, MessageDirection
from apps.customers.services import create_customer, get_customer_by_phone
from apps.services.selectors import get_services_for_business


class ConversationContext:
    def __init__(self, business, customer, conversation):
        self.business = business
        self.customer = customer
        self.conversation = conversation
        self.selected_service = None
        self.selected_staff = None
        self.selected_date = None
        self.selected_time = None


def handle_incoming_message(business, msg):
    from .adapters import send_whatsapp_message
    from .services import (
        ConversationState,
    )

    phone = msg.get("from")
    content = msg.get("text", {}).get("body", "")

    customer, _ = _get_or_create_customer(business, phone)

    conversation = _get_or_create_conversation(business, customer)

    _persist_message(conversation, MessageDirection.INBOUND, content)

    state = conversation.state or ConversationState.INITIAL

    response = _generate_response(state, content, business, customer)

    if response:
        _persist_message(conversation, MessageDirection.OUTBOUND, response)
        send_whatsapp_message(business, phone, response)

    _update_conversation_state(conversation, state, content)


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
        defaults={"state": ConversationState.INITIAL}
    )
    return conversation


def _persist_message(conversation, direction, content):
    return Message.objects.create(
        conversation=conversation,
        direction=direction,
        content=content,
    )


def _generate_response(state, content, business, customer):
    from .services import ConversationState

    content = content.strip().lower()

    if state == ConversationState.INITIAL:
        if "reserva" in content or "turno" in content or "cita" in content:
            return (
                "Hola! Vamos a gestionar tu turno. ¿Qué servicio necesitas?\n\n"
                + _list_services(business)
            )
        return "Hola! Escribe 'reserva' o 'turno' para comenzar."

    if state == ConversationState.AWAITING_SERVICE:
        return _handle_service_selection(business, content)

    if state == ConversationState.AWAITING_DATE:
        return "¿Qué fecha te gustaría? Indica el día (ej: 15/07)"

    if state == ConversationState.AWAITING_TIME:
        return "¿Qué horario te conviene? (ej: 10:00)"

    if state == ConversationState.AWAITING_CONFIRMATION:
        if "si" in content or "sí" in content:
            return "¡Turno confirmado! Te recordaremos antes del turno."
        return "Ok, el turno no fue confirmado."

    if state == ConversationState.CONFIRMED:
        return "Tu turno ya está confirmado. ¿Necesitas algo más?"

    if state == ConversationState.CANCELLED:
        return "Turno cancelado. ¿Necesitas algo más?"

    return "Lo siento, no entendí. Escribe 'reserva' para comenzar."


def _list_services(business):
    services = get_services_for_business(business)
    if not services:
        return "No hay servicios disponibles."
    lines = []
    for i, s in enumerate(services[:5], 1):
        lines.append(f"{i}. {s.name} ({s.duration_minutes} min)")
    return "\n".join(lines)


def _handle_service_selection(business, content):

    try:
        idx = int(content.strip()) - 1
        services = list(get_services_for_business(business)[:5])
        if 0 <= idx < len(services):
            return f"Perfecto, {services[idx].name}. ¿Qué fecha te gustaría?"
    except ValueError:
        pass
    return "Por favor selecciona un número de la lista de servicios."


@transaction.atomic
def _update_conversation_state(conversation, current_state, content):
    from .services import ConversationState, can_transition

    new_state = current_state

    content = content.strip().lower()

    if current_state == ConversationState.INITIAL:
        if "reserva" in content or "turno" in content or "cita" in content:
            new_state = ConversationState.AWAITING_SERVICE

    elif current_state == ConversationState.AWAITING_SERVICE:
        try:
            idx = int(content) - 1
            services = list(get_services_for_business(conversation.business)[:5])
            if 0 <= idx < len(services):
                new_state = ConversationState.AWAITING_DATE
        except ValueError:
            pass

    elif current_state == ConversationState.AWAITING_DATE:
        new_state = ConversationState.AWAITING_TIME

    elif current_state == ConversationState.AWAITING_TIME:
        new_state = ConversationState.AWAITING_CONFIRMATION

    elif current_state == ConversationState.AWAITING_CONFIRMATION:
        if "si" in content or "sí" in content:
            new_state = ConversationState.CONFIRMED
        else:
            new_state = ConversationState.INITIAL

    if new_state != current_state and can_transition(current_state, new_state):
        conversation.state = new_state
        conversation.save()
