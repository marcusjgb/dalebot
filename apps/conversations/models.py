import uuid

from django.db import models


class ConversationStatus(models.TextChoices):
    ACTIVE = "active", "Activa"
    CLOSED = "closed", "Cerrada"


class MessageDirection(models.TextChoices):
    INBOUND = "inbound", "Entrante"
    OUTBOUND = "outbound", "Saliente"


class Conversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(
        "businesses.Business",
        on_delete=models.CASCADE,
        related_name="conversations",
    )
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.CASCADE,
        related_name="conversations",
    )
    status = models.CharField(
        max_length=20,
        choices=ConversationStatus.choices,
        default=ConversationStatus.ACTIVE,
    )
    state = models.CharField(max_length=50, blank=True, default="")
    context_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "conversations"
        ordering = ["-updated_at"]


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    direction = models.CharField(
        max_length=20,
        choices=MessageDirection.choices,
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "messages"
        ordering = ["timestamp"]
