from .models import Staff


def get_staff_by_id(staff_id):
    return Staff.objects.get(id=staff_id)


def get_staff_for_business(business):
    return Staff.objects.filter(business=business, is_active=True).order_by("user__username")


def get_staff_for_service(service):
    return Staff.objects.filter(
        services=service,
        is_active=True,
    ).order_by("user__username")


def get_staff_with_services(staff_id):
    return Staff.objects.prefetch_related("services").get(id=staff_id)
