from datetime import timedelta
from unittest.mock import patch

import pytest
from django.utils import timezone

from apps.accounts.models import UserRole
from apps.accounts.services import create_user
from apps.analytics.models import DailyMetrics
from apps.analytics.tasks import update_daily_metrics
from apps.appointments.models import Appointment, AppointmentStatus
from apps.appointments.tasks import check_and_send_reminders
from apps.businesses.services import create_business
from apps.customers.services import create_customer
from apps.notifications.models import Notification, NotificationStatus, NotificationType
from apps.notifications.tasks import (
    send_appointment_cancellation,
    send_appointment_confirmation,
    send_appointment_reminder,
)
from apps.services.services import create_service
from apps.staff.services import create_staff


@pytest.fixture
def business(db):
    return create_business("Test Business Ops")


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
def staff_user(db, business):
    return create_user(
        business=business,
        username="staff",
        email="staff@test.com",
        password="test123",
        role=UserRole.STAFF,
    )


@pytest.fixture
def service(db, business):
    return create_service(
        business=business,
        name="Corte",
        duration_minutes=30,
        price=100,
    )


@pytest.fixture
def staff_member(db, business, staff_user, service):
    return create_staff(business, staff_user, service_ids=[service.id])


@pytest.fixture
def customer(db, business):
    return create_customer(
        business=business,
        name="John Doe",
        phone="+1234567890",
    )


@pytest.fixture
def confirmed_appointment(db, business, customer, service, staff_member):
    appointment = Appointment.objects.create(
        business=business,
        customer=customer,
        service=service,
        staff=staff_member,
        starts_at=timezone.now() + timedelta(days=1),
        ends_at=timezone.now() + timedelta(days=1) + timedelta(minutes=30),
        status=AppointmentStatus.CONFIRMED,
    )
    return appointment


@pytest.mark.django_db
class TestSendReminderTask:
    @patch("apps.whatsapp.adapters.send_whatsapp_message")
    def test_reminder_creates_notification(self, mock_send, confirmed_appointment):
        result = send_appointment_reminder(str(confirmed_appointment.id))

        assert result["status"] == "sent"
        notification = Notification.objects.get(appointment=confirmed_appointment)
        assert notification.notification_type == NotificationType.REMINDER
        assert notification.status == NotificationStatus.SENT

    def test_reminder_fails_for_nonexistent_appointment(self):
        import uuid
        result = send_appointment_reminder(str(uuid.uuid4()))
        assert result["status"] == "error"

    @patch("apps.whatsapp.adapters.send_whatsapp_message")
    def test_reminder_fails_for_cancelled_appointment(
        self, mock_send, business, customer, service, staff_member
    ):
        appointment = Appointment.objects.create(
            business=business,
            customer=customer,
            service=service,
            staff=staff_member,
            starts_at=timezone.now() + timedelta(days=1),
            ends_at=timezone.now() + timedelta(days=1) + timedelta(minutes=30),
            status=AppointmentStatus.CANCELLED,
        )
        result = send_appointment_reminder(str(appointment.id))
        assert result["status"] == "skipped"


@pytest.mark.django_db
class TestSendConfirmationTask:
    @patch("apps.whatsapp.adapters.send_whatsapp_message")
    def test_confirmation_creates_notification(self, mock_send, confirmed_appointment):
        result = send_appointment_confirmation(str(confirmed_appointment.id))

        assert result["status"] == "sent"
        notification = Notification.objects.get(appointment=confirmed_appointment)
        assert notification.notification_type == NotificationType.CONFIRMATION
        assert notification.status == NotificationStatus.SENT


@pytest.mark.django_db
class TestSendCancellationTask:
    @patch("apps.whatsapp.adapters.send_whatsapp_message")
    def test_cancellation_creates_notification(self, mock_send, confirmed_appointment):
        result = send_appointment_cancellation(str(confirmed_appointment.id), "Cliente solicito")

        assert result["status"] == "sent"
        notification = Notification.objects.get(appointment=confirmed_appointment)
        assert notification.notification_type == NotificationType.CANCELLATION
        assert notification.status == NotificationStatus.SENT


@pytest.mark.django_db
class TestCheckAndSendReminders:
    @patch("apps.notifications.tasks.send_appointment_reminder.delay")
    def test_check_reminders_schedules_pending(self, mock_delay, confirmed_appointment):
        check_and_send_reminders()
        mock_delay.assert_called_once_with(str(confirmed_appointment.id))


@pytest.mark.django_db
class TestUpdateDailyMetrics:
    def test_update_metrics_creates_daily_record(self, business, customer, service, staff_member):
        yesterday = timezone.now().date() - timedelta(days=1)

        Appointment.objects.create(
            business=business,
            customer=customer,
            service=service,
            staff=staff_member,
            starts_at=(
                timezone.make_aware(
                    timezone.datetime.combine(yesterday, timezone.datetime.min.time())
                )
                + timedelta(hours=10)
            ),
            ends_at=(
                timezone.make_aware(
                    timezone.datetime.combine(yesterday, timezone.datetime.min.time())
                )
                + timedelta(hours=10, minutes=30)
            ),
            status=AppointmentStatus.CONFIRMED,
        )

        result = update_daily_metrics()

        assert result["businesses_processed"] >= 1
        metrics = DailyMetrics.objects.get(business=business, date=yesterday)
        assert metrics.confirmed_appointments == 1
