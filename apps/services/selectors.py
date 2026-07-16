from .models import Service


def get_service_by_id(service_id):
    return Service.objects.get(id=service_id)


def get_services_for_business(business):
    return Service.objects.filter(business=business, is_active=True).order_by("name")


def get_active_services_for_staff(staff):
    return staff.services.filter(is_active=True).order_by("name")
