
from django.db.models import Q

from .models import AvailabilityException, AvailabilitySlot


def get_availability_slots_for_business(business):
    return AvailabilitySlot.objects.filter(business=business, is_active=True)


def get_availability_slots_for_staff(staff):
    return AvailabilitySlot.objects.filter(
        Q(staff=staff) | Q(staff__isnull=True),
        is_active=True,
    )


def get_availability_slots_for_day(business, day_of_week, staff=None):
    qs = AvailabilitySlot.objects.filter(
        business=business,
        day_of_week=day_of_week,
        is_active=True,
    )
    if staff:
        qs = qs.filter(Q(staff=staff) | Q(staff__isnull=True))
    return qs


def get_exceptions_for_date(business, target_date, staff=None):
    qs = AvailabilityException.objects.filter(
        business=business,
        date=target_date,
    )
    if staff:
        qs = qs.filter(Q(staff=staff) | Q(staff__isnull=True))
    return qs


def is_slot_available(business, target_date, start_time, end_time, staff=None):
    day_of_week = target_date.weekday()

    slots = get_availability_slots_for_day(business, day_of_week, staff)
    if not slots.exists():
        return False

    slot_match = False
    for slot in slots:
        if slot.start_time <= start_time and slot.end_time >= end_time:
            slot_match = True
            break

    if not slot_match:
        return False

    exceptions = get_exceptions_for_date(business, target_date, staff)
    for exc in exceptions:
        if exc.is_available:
            if exc.start_time and exc.end_time:
                if not (end_time <= exc.start_time or start_time >= exc.end_time):
                    return True
            else:
                return False
        else:
            return False

    return True
