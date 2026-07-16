import logging
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

logger = logging.getLogger(__name__)


class AppointmentError(Exception):
    pass


class SlotNotAvailableError(AppointmentError):
    pass


class StaffNotAssignedToServiceError(AppointmentError):
    pass


class AppointmentOverlapError(AppointmentError):
    pass


def _validate_staff_service_assignment(staff, service):
    if not staff.services.filter(id=service.id, is_active=True).exists():
        raise StaffNotAssignedToServiceError(
            f"Staff {staff.id} is not assigned to service {service.id}"
        )


def _validate_availability(business, date, start_time, end_time, staff):
    from apps.availability.selectors import is_slot_available
    if not is_slot_available(business, date, start_time, end_time, staff):
        raise SlotNotAvailableError(
            f"Slot not available for staff {staff.id} on {date}"
        )


def _validate_no_overlap(staff, starts_at, ends_at, exclude_appointment_id=None):
    from .models import Appointment, AppointmentStatus
    overlaps = Appointment.objects.filter(
        staff=staff,
        status__in=[AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED],
        starts_at__lt=ends_at,
        ends_at__gt=starts_at,
    )
    if exclude_appointment_id:
        overlaps = overlaps.exclude(id=exclude_appointment_id)

    if overlaps.exists():
        raise AppointmentOverlapError(
            f"Staff {staff.id} already has an appointment at this time"
        )


def _schedule_reminder(appointment):
    from apps.notifications.tasks import send_appointment_reminder
    send_appointment_reminder.apply_async(
        args=[str(appointment.id)],
        eta=appointment.starts_at - timezone.timedelta(hours=24),
    )


def _log_audit(user, business, action, entity, changes=None):
    from apps.audit.services import log_action
    try:
        log_action(
            user=user,
            business=business,
            action=action,
            entity_type=entity.__class__.__name__,
            entity_id=getattr(entity, "id", None),
            changes=changes or {},
        )
    except Exception as exc:
        logger.warning(f"Failed to log audit: {exc}")


@transaction.atomic
def create_appointment(business, customer, service, staff, starts_at, notes="", user=None):
    from .models import Appointment, AppointmentStatus

    ends_at = starts_at + timedelta(minutes=service.duration_minutes)

    _validate_staff_service_assignment(staff, service)
    _validate_availability(business, starts_at.date(), starts_at.time(), ends_at.time(), staff)
    _validate_no_overlap(staff, starts_at, ends_at)

    appointment = Appointment.objects.create(
        business=business,
        customer=customer,
        service=service,
        staff=staff,
        starts_at=starts_at,
        ends_at=ends_at,
        status=AppointmentStatus.PENDING,
        notes=notes,
    )

    _log_audit(user, business, "create", appointment)

    return appointment


@transaction.atomic
def confirm_appointment(appointment, user=None):
    from .models import AppointmentStatus
    if appointment.status != AppointmentStatus.PENDING:
        raise AppointmentError(f"Cannot confirm appointment with status {appointment.status}")

    appointment.status = AppointmentStatus.CONFIRMED
    appointment.save()

    _log_audit(user, appointment.business, "confirm", appointment)

    try:
        from apps.notifications.tasks import send_appointment_confirmation
        send_appointment_confirmation.delay(str(appointment.id))
    except Exception as exc:
        logger.warning(f"Failed to schedule confirmation notification: {exc}")

    return appointment


@transaction.atomic
def cancel_appointment(appointment, cancelled_by, reason=""):
    from .models import AppointmentStatus
    if appointment.status == AppointmentStatus.CANCELLED:
        raise AppointmentError("Appointment is already cancelled")

    appointment.status = AppointmentStatus.CANCELLED
    appointment.cancelled_by = cancelled_by
    appointment.cancelled_at = timezone.now()
    appointment.cancellation_reason = reason
    appointment.save()

    _log_audit(cancelled_by, appointment.business, "cancel", appointment, {"reason": reason})

    try:
        from apps.notifications.tasks import send_appointment_cancellation
        send_appointment_cancellation.delay(str(appointment.id), reason)
    except Exception as exc:
        logger.warning(f"Failed to schedule cancellation notification: {exc}")

    return appointment


@transaction.atomic
def reschedule_appointment(appointment, new_starts_at, rescheduled_by):
    from .models import AppointmentStatus

    if appointment.status not in [AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED]:
        raise AppointmentError(f"Cannot reschedule appointment with status {appointment.status}")

    old_starts_at = appointment.starts_at
    ends_at = new_starts_at + timedelta(minutes=appointment.service.duration_minutes)

    _validate_availability(
        appointment.business,
        new_starts_at.date(),
        new_starts_at.time(),
        ends_at.time(),
        appointment.staff,
    )
    _validate_no_overlap(
        appointment.staff,
        new_starts_at,
        ends_at,
        exclude_appointment_id=appointment.id,
    )

    appointment.starts_at = new_starts_at
    appointment.ends_at = ends_at
    appointment.save()

    _log_audit(
        rescheduled_by,
        appointment.business,
        "reschedule",
        appointment,
        {"old_starts_at": str(old_starts_at), "new_starts_at": str(new_starts_at)},
    )

    return appointment


@transaction.atomic
def update_appointment(appointment, user=None, customer=None, service=None, staff=None,
                       starts_at=None, notes=None):
    from .models import AppointmentStatus

    if appointment.status not in [AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED]:
        raise AppointmentError(f"Cannot update appointment with status {appointment.status}")

    changes = {}

    if customer is not None and customer != appointment.customer:
        changes["customer"] = {"old": str(appointment.customer), "new": str(customer)}
        appointment.customer = customer

    if service is not None and service != appointment.service:
        changes["service"] = {"old": str(appointment.service), "new": str(service)}
        appointment.service = service

    if staff is not None and staff != appointment.staff:
        changes["staff"] = {"old": str(appointment.staff), "new": str(staff)}
        appointment.staff = staff

    if starts_at is not None and starts_at != appointment.starts_at:
        changes["starts_at"] = {"old": str(appointment.starts_at), "new": str(starts_at)}
        appointment.starts_at = starts_at
        appointment.ends_at = starts_at + timedelta(minutes=appointment.service.duration_minutes)

    if notes is not None and notes != appointment.notes:
        changes["notes"] = {"old": appointment.notes or "", "new": notes}
        appointment.notes = notes

    if changes:
        appointment.save()
        _log_audit(user, appointment.business, "update", appointment, changes)

    return appointment


@transaction.atomic
def complete_appointment(appointment, user=None):
    from .models import AppointmentStatus
    if appointment.status != AppointmentStatus.CONFIRMED:
        raise AppointmentError(f"Cannot complete appointment with status {appointment.status}")
    appointment.status = AppointmentStatus.COMPLETED
    appointment.save()

    _log_audit(user, appointment.business, "complete", appointment)

    return appointment


@transaction.atomic
def mark_no_show(appointment, user=None):
    from .models import AppointmentStatus
    if appointment.status != AppointmentStatus.CONFIRMED:
        raise AppointmentError(
            f"Cannot mark no-show for appointment with status {appointment.status}"
        )
    appointment.status = AppointmentStatus.NO_SHOW
    appointment.save()

    _log_audit(user, appointment.business, "no_show", appointment)

    return appointment
