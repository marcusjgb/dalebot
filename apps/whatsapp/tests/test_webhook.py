from unittest.mock import patch

import pytest
from django.urls import reverse

from apps.accounts.models import UserRole
from apps.accounts.services import create_user
from apps.businesses.services import create_business
from apps.whatsapp.models import WhatsAppBusinessAccount, WhatsAppEvent
from apps.whatsapp.services import (
    ConversationState,
    can_transition,
    process_webhook_event,
)


@pytest.fixture
def business(db):
    return create_business("Test Business WhatsApp")


@pytest.fixture
def owner(db, business):
    return create_user(
        business=business,
        username="owner",
        email="owner@test.com",
        password="test123",
        role=UserRole.OWNER,
    )


@pytest.fixture
def whatsapp_account(db, business):
    return WhatsAppBusinessAccount.objects.create(
        business=business,
        phone_number_id="123456789",
        phone_number="+5491112345678",
        verified_name="Test Business",
    )


@pytest.fixture
def webhook_payload(whatsapp_account):
    return {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "123456789",
            "changes": [{
                "value": {
                    "metadata": {
                        "phone_number_id": "123456789"
                    },
                    "messages": [{
                        "id": "wamid.test123",
                        "from": "+5491112345678",
                        "type": "text",
                        "text": {"body": "Hola, quiero reservar un turno"},
                    }]
                },
                "change": "messages"
            }]
        }]
    }


@pytest.mark.django_db
class TestWebhookIdempotency:
    def test_webhook_returns_200_for_valid_request(self, client, webhook_payload):
        with patch("apps.whatsapp.webhooks.verify_meta_signature", return_value=True):
            response = client.post(
                reverse("whatsapp_webhook"),
                data=webhook_payload,
                content_type="application/json",
            )
        assert response.status_code == 200

    def test_webhook_returns_403_for_invalid_signature(self, client, webhook_payload):
        with patch("apps.whatsapp.webhooks.verify_meta_signature", return_value=False):
            response = client.post(
                reverse("whatsapp_webhook"),
                data=webhook_payload,
                content_type="application/json",
            )
        assert response.status_code == 403

    def test_duplicate_event_not_processed_twice(self, business, whatsapp_account, webhook_payload):
        event_id = webhook_payload["entry"][0]["changes"][0]["value"]["messages"][0]["id"]

        WhatsAppEvent.objects.create(
            event_id=event_id,
            business=business,
            event_type="message",
            payload={},
            processed=True,
        )

        result = process_webhook_event(webhook_payload)
        assert result["status"] == "duplicate"


@pytest.mark.django_db
class TestConversationStateMachine:
    def test_initial_to_awaiting_service_transition(self):
        assert can_transition(ConversationState.INITIAL, ConversationState.AWAITING_SERVICE)

    def test_invalid_transition(self):
        assert not can_transition(ConversationState.INITIAL, ConversationState.CONFIRMED)

    def test_confirmed_to_cancelled_transition(self):
        assert can_transition(ConversationState.CONFIRMED, ConversationState.CANCELLED)

    def test_no_self_transition_from_confirmed(self):
        assert not can_transition(ConversationState.CONFIRMED, ConversationState.CONFIRMED)
