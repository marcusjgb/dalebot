from django.db import transaction


@transaction.atomic
def log_action(
    user=None,
    business=None,
    action=None,
    entity_type=None,
    entity_id=None,
    changes=None,
    ip_address=None,
    user_agent=None,
):
    from .models import AuditLog

    return AuditLog.objects.create(
        user=user,
        business=business,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        changes=changes or {},
        ip_address=ip_address,
        user_agent=user_agent or "",
    )


@transaction.atomic
def log_create(user, business, entity, changes=None):
    return log_action(
        user=user,
        business=business,
        action="create",
        entity_type=entity.__class__.__name__,
        entity_id=getattr(entity, "id", None),
        changes=changes,
    )


@transaction.atomic
def log_update(user, business, entity, changes=None):
    return log_action(
        user=user,
        business=business,
        action="update",
        entity_type=entity.__class__.__name__,
        entity_id=getattr(entity, "id", None),
        changes=changes,
    )


@transaction.atomic
def log_delete(user, business, entity_type, entity_id, changes=None):
    return log_action(
        user=user,
        business=business,
        action="delete",
        entity_type=entity_type,
        entity_id=entity_id,
        changes=changes,
    )


def log_appointment_cancellation(user, appointment, reason):
    return log_action(
        user=user,
        business=appointment.business,
        action="cancel",
        entity_type="Appointment",
        entity_id=appointment.id,
        changes={"reason": reason, "previous_status": appointment.status},
    )


def log_appointment_reschedule(user, appointment, old_starts_at, new_starts_at):
    return log_action(
        user=user,
        business=appointment.business,
        action="reschedule",
        entity_type="Appointment",
        entity_id=appointment.id,
        changes={
            "old_starts_at": str(old_starts_at),
            "new_starts_at": str(new_starts_at),
        },
    )
