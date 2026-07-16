from datetime import timedelta

from django.utils import timezone


def get_business_metrics(business, days=30):
    from apps.appointments.models import Appointment, AppointmentStatus
    from apps.conversations.models import Conversation
    from apps.customers.models import Customer

    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)

    appointments = Appointment.objects.filter(
        business=business,
        created_at__gte=start_date,
    )

    total = appointments.count()
    confirmed = appointments.filter(status=AppointmentStatus.CONFIRMED).count()
    cancelled = appointments.filter(status=AppointmentStatus.CANCELLED).count()
    completed = appointments.filter(status=AppointmentStatus.COMPLETED).count()

    conversion_rate = (confirmed / total * 100) if total > 0 else 0

    new_customers = Customer.objects.filter(
        business=business,
        created_at__gte=start_date,
    ).count()

    conversations = Conversation.objects.filter(
        business=business,
        created_at__gte=start_date,
    ).count()

    return {
        "period_days": days,
        "total_appointments": total,
        "confirmed_appointments": confirmed,
        "cancelled_appointments": cancelled,
        "completed_appointments": completed,
        "conversion_rate": round(conversion_rate, 2),
        "new_customers": new_customers,
        "conversations": conversations,
    }


def get_business_summary(business):
    from apps.customers.models import Customer
    from apps.services.models import Service
    from apps.staff.models import Staff

    return {
        "active_services": Service.objects.filter(business=business, is_active=True).count(),
        "active_staff": Staff.objects.filter(business=business, is_active=True).count(),
        "total_customers": Customer.objects.filter(business=business, is_active=True).count(),
    }


def get_conversion_metrics(business, days=30):
    from apps.appointments.models import Appointment, AppointmentStatus

    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)

    total_conversations = Appointment.objects.filter(
        business=business,
        created_at__gte=start_date,
    ).count()

    converted = Appointment.objects.filter(
        business=business,
        created_at__gte=start_date,
        status__in=[AppointmentStatus.CONFIRMED, AppointmentStatus.COMPLETED],
    ).count()

    return {
        "total_conversations": total_conversations,
        "converted_to_appointment": converted,
        "conversion_rate": round(
            (converted / total_conversations * 100)
            if total_conversations > 0
            else 0,
            2,
        ),
    }
