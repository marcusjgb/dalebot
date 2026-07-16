from celery import shared_task
from django.utils import timezone


@shared_task
def check_and_send_reminders():
    from apps.appointments.models import Appointment, AppointmentStatus
    from apps.notifications.tasks import send_appointment_reminder

    reminder_window = timezone.now() + timezone.timedelta(hours=25)

    appointments = Appointment.objects.filter(
        status__in=[AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED],
        starts_at__lte=reminder_window,
        starts_at__gte=timezone.now(),
    ).select_related("business", "customer", "service", "staff")

    results = []
    for appointment in appointments:
        try:
            send_appointment_reminder.delay(str(appointment.id))
            results.append({"id": str(appointment.id), "status": "scheduled"})
        except Exception as exc:
            results.append({"id": str(appointment.id), "status": "error", "error": str(exc)})

    return results
