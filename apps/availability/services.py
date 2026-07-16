from django.db import transaction


@transaction.atomic
def create_availability_slot(business, day_of_week, start_time, end_time, staff=None):
    from .models import AvailabilitySlot
    return AvailabilitySlot.objects.create(
        business=business,
        staff=staff,
        day_of_week=day_of_week,
        start_time=start_time,
        end_time=end_time,
    )


@transaction.atomic
def update_availability_slot(slot, **kwargs):
    allowed = ["start_time", "end_time", "is_active"]
    for key, value in kwargs.items():
        if key in allowed:
            setattr(slot, key, value)
    slot.save()
    return slot


@transaction.atomic
def delete_availability_slot(slot):
    slot.delete()


@transaction.atomic
def create_availability_exception(
    business,
    date,
    is_available,
    staff=None,
    start_time=None,
    end_time=None,
    reason="",
):
    from .models import AvailabilityException
    return AvailabilityException.objects.create(
        business=business,
        staff=staff,
        date=date,
        start_time=start_time,
        end_time=end_time,
        is_available=is_available,
        reason=reason,
    )


@transaction.atomic
def delete_availability_exception(exception):
    exception.delete()
