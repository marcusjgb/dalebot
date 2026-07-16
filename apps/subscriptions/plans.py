from .models import PlanType

PLAN_LIMITS = {
    PlanType.FREE: {
        "staff_limit": 1,
        "services_limit": 3,
        "appointments_per_month": 50,
        "customers_limit": 100,
        "notifications_enabled": True,
        "whatsapp_enabled": True,
    },
    PlanType.BASIC: {
        "staff_limit": 3,
        "services_limit": 10,
        "appointments_per_month": 200,
        "customers_limit": 500,
        "notifications_enabled": True,
        "whatsapp_enabled": True,
    },
    PlanType.PRO: {
        "staff_limit": 10,
        "services_limit": 50,
        "appointments_per_month": 1000,
        "customers_limit": 2000,
        "notifications_enabled": True,
        "whatsapp_enabled": True,
    },
}


def get_plan_limits(plan_type):
    return PLAN_LIMITS.get(plan_type, PLAN_LIMITS[PlanType.FREE])


def check_staff_limit(business):
    from apps.staff.models import Staff
    limit = get_plan_limits(business.subscription.plan)["staff_limit"]
    current = Staff.objects.filter(business=business, is_active=True).count()
    return current < limit


def check_services_limit(business):
    from apps.services.models import Service
    limit = get_plan_limits(business.subscription.plan)["services_limit"]
    current = Service.objects.filter(business=business, is_active=True).count()
    return current < limit


def check_customers_limit(business):
    from apps.customers.models import Customer
    limit = get_plan_limits(business.subscription.plan)["customers_limit"]
    current = Customer.objects.filter(business=business, is_active=True).count()
    return current < limit


def check_appointments_limit(business):

    from django.utils import timezone

    from apps.appointments.models import Appointment

    limit = get_plan_limits(business.subscription.plan)["appointments_per_month"]
    month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    current = Appointment.objects.filter(
        business=business,
        created_at__gte=month_start,
    ).count()
    return current < limit
