from django.db import transaction
from django.utils import timezone


class ConversationState:
    INITIAL = "initial"
    AWAITING_SERVICE = "awaiting_service"
    AWAITING_STAFF = "awaiting_staff"
    AWAITING_DATE = "awaiting_date"
    AWAITING_TIME = "awaiting_time"
    AWAITING_CONFIRMATION = "awaiting_confirmation"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


STATE_TRANSITIONS = {
    ConversationState.INITIAL: [ConversationState.AWAITING_SERVICE],
    ConversationState.AWAITING_SERVICE: [
        ConversationState.AWAITING_STAFF,
        ConversationState.AWAITING_DATE,
    ],
    ConversationState.AWAITING_STAFF: [ConversationState.AWAITING_DATE],
    ConversationState.AWAITING_DATE: [ConversationState.AWAITING_TIME],
    ConversationState.AWAITING_TIME: [ConversationState.AWAITING_CONFIRMATION],
    ConversationState.AWAITING_CONFIRMATION: [
        ConversationState.CONFIRMED,
        ConversationState.CANCELLED,
    ],
    ConversationState.CONFIRMED: [ConversationState.CANCELLED],
}


def can_transition(from_state, to_state):
    return to_state in STATE_TRANSITIONS.get(from_state, [])


@transaction.atomic
def process_webhook_event(payload):
    from .models import WhatsAppBusinessAccount, WhatsAppEvent

    entry = payload.get("entry", [])
    if not entry:
        return {"status": "error", "error": "No entry in payload"}

    for e in entry:
        changes = e.get("changes", [])
        for change in changes:
            value = change.get("value", {})
            metadata = value.get("metadata", {})

            phone_number_id = metadata.get("phone_number_id")
            if not phone_number_id:
                continue

            try:
                account = WhatsAppBusinessAccount.objects.get(
                    phone_number_id=phone_number_id,
                    is_active=True,
                )
            except WhatsAppBusinessAccount.DoesNotExist:
                continue

            business = account.business

            messages = value.get("messages", [])
            for msg in messages:
                event_id = msg.get("id")
                if not event_id:
                    continue

                event, created = WhatsAppEvent.objects.get_or_create(
                    event_id=event_id,
                    defaults={
                        "business": business,
                        "event_type": "message",
                        "payload": msg,
                    }
                )

                if not created and event.processed:
                    return {"status": "duplicate"}

                _process_message(business, msg, event)

    return {"status": "ok"}


def _process_message(business, msg, event):
    from .handlers import handle_incoming_message

    try:
        handle_incoming_message(business, msg)
        event.processed = True
        event.processed_at = timezone.now()
    except Exception as exc:
        event.error_message = str(exc)
    event.save()
