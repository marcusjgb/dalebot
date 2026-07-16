from celery import shared_task
from django.utils import timezone


@shared_task
def send_appointment_reminder(appointment_id):
    from apps.appointments.models import Appointment, AppointmentStatus
    from apps.notifications.models import Notification, NotificationStatus, NotificationType
    from apps.whatsapp.adapters import send_whatsapp_message

    try:
        appointment = Appointment.objects.select_related(
            "business", "customer", "service", "staff"
        ).get(id=appointment_id)
    except Appointment.DoesNotExist:
        return {"status": "error", "error": "Appointment not found"}

    if appointment.status not in [AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED]:
        return {"status": "skipped", "reason": "Appointment not active"}

    reminder_time = appointment.starts_at - timezone.timedelta(hours=24)
    if timezone.now() < reminder_time:
        return {"status": "scheduled", "scheduled_for": reminder_time}

    notification = Notification.objects.create(
        business=appointment.business,
        appointment=appointment,
        notification_type=NotificationType.REMINDER,
        channel="whatsapp",
        status=NotificationStatus.PENDING,
        scheduled_for=appointment.starts_at - timezone.timedelta(hours=24),
    )

    try:
        staff_name = (
            appointment.staff.user.get_full_name()
            or appointment.staff.user.username
        )
        message = (
            f"Hola {appointment.customer.name}, te recordamos tu turno mañana "
            f"({appointment.starts_at.strftime('%d/%m/%Y %H:%M')}) "
            f"para {appointment.service.name} con {staff_name}."
        )
        send_whatsapp_message(appointment.business, appointment.customer.phone, message)

        notification.status = NotificationStatus.SENT
        notification.sent_at = timezone.now()
        notification.save()

        return {"status": "sent", "notification_id": str(notification.id)}

    except Exception as exc:
        notification.status = NotificationStatus.FAILED
        notification.error_message = str(exc)
        notification.save()
        return {"status": "error", "error": str(exc)}


@shared_task
def send_appointment_confirmation(appointment_id):
    from apps.appointments.models import Appointment, AppointmentStatus
    from apps.notifications.models import Notification, NotificationStatus, NotificationType
    from apps.whatsapp.adapters import send_whatsapp_message

    try:
        appointment = Appointment.objects.select_related(
            "business", "customer", "service", "staff"
        ).get(id=appointment_id)
    except Appointment.DoesNotExist:
        return {"status": "error", "error": "Appointment not found"}

    if appointment.status != AppointmentStatus.CONFIRMED:
        return {"status": "skipped", "reason": "Appointment not confirmed"}

    notification = Notification.objects.create(
        business=appointment.business,
        appointment=appointment,
        notification_type=NotificationType.CONFIRMATION,
        channel="whatsapp",
        status=NotificationStatus.PENDING,
        scheduled_for=timezone.now(),
    )

    try:
        message = (
            f"¡Turno confirmado! {appointment.service.name} "
            f"el {appointment.starts_at.strftime('%d/%m/%Y a las %H:%M')} "
            f"con {appointment.staff.user.get_full_name() or appointment.staff.user.username}."
        )
        send_whatsapp_message(appointment.business, appointment.customer.phone, message)

        notification.status = NotificationStatus.SENT
        notification.sent_at = timezone.now()
        notification.save()

        return {"status": "sent", "notification_id": str(notification.id)}

    except Exception as exc:
        notification.status = NotificationStatus.FAILED
        notification.error_message = str(exc)
        notification.save()
        return {"status": "error", "error": str(exc)}


@shared_task
def send_appointment_cancellation(appointment_id, reason=""):
    from apps.appointments.models import Appointment
    from apps.notifications.models import Notification, NotificationStatus, NotificationType
    from apps.whatsapp.adapters import send_whatsapp_message

    try:
        appointment = Appointment.objects.select_related(
            "business", "customer", "service", "staff"
        ).get(id=appointment_id)
    except Appointment.DoesNotExist:
        return {"status": "error", "error": "Appointment not found"}

    notification = Notification.objects.create(
        business=appointment.business,
        appointment=appointment,
        notification_type=NotificationType.CANCELLATION,
        channel="whatsapp",
        status=NotificationStatus.PENDING,
        scheduled_for=timezone.now(),
    )

    try:
        reason_text = f" Motivo: {reason}" if reason else ""
        message = (
            f"Tu turno para {appointment.service.name} "
            f"el {appointment.starts_at.strftime('%d/%m/%Y')} ha sido cancelado.{reason_text}"
        )
        send_whatsapp_message(appointment.business, appointment.customer.phone, message)

        notification.status = NotificationStatus.SENT
        notification.sent_at = timezone.now()
        notification.save()

        return {"status": "sent", "notification_id": str(notification.id)}

    except Exception as exc:
        notification.status = NotificationStatus.FAILED
        notification.error_message = str(exc)
        notification.save()
        return {"status": "error", "error": str(exc)}
