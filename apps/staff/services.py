from django.db import transaction


@transaction.atomic
def create_staff(business, user, service_ids=None):
    from .models import Staff
    staff = Staff.objects.create(
        business=business,
        user=user,
    )
    if service_ids:
        staff.services.set(service_ids)
    return staff


@transaction.atomic
def update_staff(staff, **kwargs):
    allowed = ["is_active"]
    if "service_ids" in kwargs:
        staff.services.set(kwargs.pop("service_ids"))
    for key, value in kwargs.items():
        if key in allowed:
            setattr(staff, key, value)
    staff.save()
    return staff


@transaction.atomic
def deactivate_staff(staff):
    staff.is_active = False
    staff.save()
    return staff


def add_service_to_staff(staff, service):
    staff.services.add(service)


def remove_service_from_staff(staff, service):
    staff.services.remove(service)
