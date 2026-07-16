import uuid

from django.db import models


class PlanType(models.TextChoices):
    FREE = "free", "Gratis"
    BASIC = "basic", "Básico"
    PRO = "pro", "Profesional"


class SubscriptionStatus(models.TextChoices):
    ACTIVE = "active", "Activa"
    CANCELLED = "cancelled", "Cancelada"
    EXPIRED = "expired", "Vencida"


class Subscription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.OneToOneField(
        "businesses.Business",
        on_delete=models.CASCADE,
        related_name="subscription",
    )
    plan = models.CharField(
        max_length=20,
        choices=PlanType.choices,
        default=PlanType.FREE,
    )
    status = models.CharField(
        max_length=20,
        choices=SubscriptionStatus.choices,
        default=SubscriptionStatus.ACTIVE,
    )
    starts_at = models.DateTimeField(auto_now_add=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "subscriptions"

    def __str__(self):
        return f"{self.business.name} - {self.plan}"
