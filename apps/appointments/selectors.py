
from .models import Appointment, AppointmentStatus


def get_appointment_by_id(appointment_id):
    return Appointment.objects.get(id=appointment_id)


def get_appointments_for_business(business, status=None):
    qs = Appointment.objects.filter(business=business)
    if status:
        qs = qs.filter(status=status)
    return qs.order_by("-starts_at")


def get_appointments_for_customer(customer):
    return Appointment.objects.filter(customer=customer).order_by("-starts_at")


def get_appointments_for_staff(staff, date=None):
    qs = Appointment.objects.filter(staff=staff)
    if date:
        qs = qs.filter(starts_at__date=date)
    return qs.order_by("starts_at")


def get_upcoming_appointments_for_business(business):
    from django.utils import timezone
    return Appointment.objects.filter(
        business=business,
        starts_at__gte=timezone.now(),
        status__in=[AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED],
    ).order_by("starts_at")


def get_daily_appointments(business, date):
    return Appointment.objects.filter(
        business=business,
        starts_at__date=date,
    ).order_by("starts_at")
