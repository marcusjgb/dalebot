from datetime import date, time, timedelta

import pytest
from django.utils import timezone

from apps.accounts.models import UserRole
from apps.accounts.services import create_user
from apps.appointments.models import AppointmentStatus
from apps.appointments.services import (
    AppointmentOverlapError,
    StaffNotAssignedToServiceError,
    cancel_appointment,
    create_appointment,
    reschedule_appointment,
)
from apps.availability.services import (
    create_availability_slot,
)
from apps.businesses.services import create_business
from apps.customers.services import create_customer
from apps.services.services import create_service
from apps.staff.services import create_staff


@pytest.fixture
def business(db):
    return create_business("Test Business", "America/New_York")


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
        name="Corte de pelo",
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
def availability(db, business, staff_member):
    create_availability_slot(
        business=business,
        staff=staff_member,
        day_of_week=0,
        start_time=time(9, 0),
        end_time=time(17, 0),
    )
    return staff_member


def make_appointment_dt(day_offset=0, hour=10, minute=0):
    d = date.today() + timedelta(days=day_offset)
    while d.weekday() != 0:
        d += timedelta(days=1)
    d += timedelta(days=day_offset)
    return timezone.make_aware(timezone.datetime.combine(d, time(hour, minute)))


@pytest.mark.django_db
class TestAppointmentCreation:
    def test_create_appointment_success(
        self, business, customer, service, staff_member, availability
    ):
        starts_at = make_appointment_dt()
        appointment = create_appointment(
            business=business,
            customer=customer,
            service=service,
            staff=staff_member,
            starts_at=starts_at,
        )
        assert appointment.id is not None
        assert appointment.ends_at == starts_at + timedelta(minutes=30)
        assert appointment.status == AppointmentStatus.PENDING

    def test_appointment_duration_from_service(
        self, business, customer, service, staff_member, availability
    ):
        service.duration_minutes = 60
        service.save()
        starts_at = make_appointment_dt()
        appointment = create_appointment(
            business=business,
            customer=customer,
            service=service,
            staff=staff_member,
            starts_at=starts_at,
        )
        assert appointment.ends_at == starts_at + timedelta(minutes=60)

    def test_appointment_fails_if_staff_not_assigned_to_service(
        self, business, customer, service, staff_member, availability
    ):
        staff_member.services.clear()
        staff_member.save()
        starts_at = make_appointment_dt()
        with pytest.raises(StaffNotAssignedToServiceError):
            create_appointment(
                business=business,
                customer=customer,
                service=service,
                staff=staff_member,
                starts_at=starts_at,
            )


@pytest.mark.django_db
class TestAppointmentOverlap:
    def test_cannot_overlap_same_staff(
        self, business, customer, service, staff_member, availability
    ):
        starts_at = make_appointment_dt()
        create_appointment(
            business=business,
            customer=customer,
            service=service,
            staff=staff_member,
            starts_at=starts_at,
        )
        with pytest.raises(AppointmentOverlapError):
            create_appointment(
                business=business,
                customer=customer,
                service=service,
                staff=staff_member,
                starts_at=starts_at + timedelta(minutes=15),
            )


@pytest.mark.django_db
class TestAppointmentCancellation:
    def test_cancel_appointment_records_actor_and_reason(
        self, business, customer, service, staff_member, availability, owner
    ):
        starts_at = make_appointment_dt()
        appointment = create_appointment(
            business=business,
            customer=customer,
            service=service,
            staff=staff_member,
            starts_at=starts_at,
        )
        cancelled = cancel_appointment(appointment, owner, "Cliente solicito cancelar")
        assert cancelled.status == AppointmentStatus.CANCELLED
        assert cancelled.cancelled_by == owner
        assert cancelled.cancellation_reason == "Cliente solicito cancelar"
        assert cancelled.cancelled_at is not None


@pytest.mark.django_db
class TestAppointmentReschedule:
    def test_reschedule_updates_times(
        self, business, customer, service, staff_member, availability, owner
    ):
        starts_at = make_appointment_dt(hour=10)
        appointment = create_appointment(
            business=business,
            customer=customer,
            service=service,
            staff=staff_member,
            starts_at=starts_at,
        )
        new_starts_at = make_appointment_dt(hour=14)
        rescheduled = reschedule_appointment(appointment, new_starts_at, owner)
        assert rescheduled.starts_at == new_starts_at
        assert rescheduled.ends_at == new_starts_at + timedelta(minutes=30)
