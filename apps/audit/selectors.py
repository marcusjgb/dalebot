from .models import AuditLog


def get_audit_logs_for_business(business, entity_type=None, user_id=None):
    qs = AuditLog.objects.filter(business=business)
    if entity_type:
        qs = qs.filter(entity_type=entity_type)
    if user_id:
        qs = qs.filter(user_id=user_id)
    return qs.order_by("-timestamp")


def get_audit_logs_for_entity(entity_type, entity_id):
    return AuditLog.objects.filter(
        entity_type=entity_type,
        entity_id=entity_id,
    ).order_by("-timestamp")
