from celery import shared_task
from django.utils import timezone


@shared_task
def update_daily_metrics():
    from apps.analytics.models import DailyMetrics
    from apps.appointments.models import Appointment, AppointmentStatus
    from apps.businesses.models import Business
    from apps.customers.models import Customer

    yesterday = timezone.now().date() - timezone.timedelta(days=1)

    for business in Business.objects.filter(is_active=True):
        appointments = Appointment.objects.filter(
            business=business,
            starts_at__date=yesterday,
        )

        metrics, _ = DailyMetrics.objects.update_or_create(
            business=business,
            date=yesterday,
            defaults={
                "total_appointments": appointments.count(),
                "confirmed_appointments": appointments.filter(
                    status=AppointmentStatus.CONFIRMED
                ).count(),
                "cancelled_appointments": appointments.filter(
                    status=AppointmentStatus.CANCELLED
                ).count(),
                "completed_appointments": appointments.filter(
                    status=AppointmentStatus.COMPLETED
                ).count(),
                "no_show_appointments": appointments.filter(
                    status=AppointmentStatus.NO_SHOW
                ).count(),
                "new_customers": Customer.objects.filter(
                    business=business,
                    created_at__date=yesterday,
                ).count(),
            },
        )

    return {
        "date": str(yesterday),
        "businesses_processed": Business.objects.filter(is_active=True).count(),
    }
