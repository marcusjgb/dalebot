
import pytest

from apps.accounts.models import UserRole
from apps.accounts.services import create_user
from apps.businesses.onboarding import (
    OnboardingError,
    onboard_business,
)
from apps.businesses.services import create_business
from apps.services.services import create_service
from apps.staff.services import create_staff
from apps.subscriptions.models import PlanType, SubscriptionStatus
from apps.subscriptions.plans import (
    check_services_limit,
    check_staff_limit,
    get_plan_limits,
)
from apps.subscriptions.services import (
    create_subscription,
    upgrade_subscription,
)


@pytest.fixture
def business(db):
    return create_business("Test Business SaaS")


@pytest.fixture
def subscription(db, business):
    return create_subscription(business, plan=PlanType.FREE)


@pytest.fixture
def owner(db, business):
    return create_user(
        business=business,
        username="owner",
        email="owner@test.com",
        password="test123",
        role=UserRole.OWNER,
    )


@pytest.mark.django_db
class TestPlanLimits:
    def test_free_plan_has_correct_limits(self):
        limits = get_plan_limits(PlanType.FREE)
        assert limits["staff_limit"] == 1
        assert limits["services_limit"] == 3
        assert limits["appointments_per_month"] == 50

    def test_basic_plan_has_correct_limits(self):
        limits = get_plan_limits(PlanType.BASIC)
        assert limits["staff_limit"] == 3
        assert limits["services_limit"] == 10
        assert limits["appointments_per_month"] == 200

    def test_pro_plan_has_correct_limits(self):
        limits = get_plan_limits(PlanType.PRO)
        assert limits["staff_limit"] == 10
        assert limits["services_limit"] == 50
        assert limits["appointments_per_month"] == 1000


@pytest.mark.django_db
class TestSubscriptionCreation:
    def test_create_free_subscription(self, business):
        subscription = create_subscription(business, plan=PlanType.FREE)
        assert subscription.plan == PlanType.FREE
        assert subscription.status == SubscriptionStatus.ACTIVE

    def test_cannot_create_duplicate_subscription(self, business, subscription):
        with pytest.raises(ValueError, match="already has a subscription"):
            create_subscription(business, PlanType.BASIC)


@pytest.mark.django_db
class TestSubscriptionUpgrade:
    def test_upgrade_from_free_to_basic(self, subscription):
        upgraded = upgrade_subscription(subscription, PlanType.BASIC)
        assert upgraded.plan == PlanType.BASIC

    def test_upgrade_logs_audit(self, subscription):
        upgrade_subscription(subscription, PlanType.BASIC)
        from apps.audit.models import AuditLog
        log = AuditLog.objects.filter(entity_id=subscription.id).first()
        assert log is not None
        assert "upgrade_plan" in str(log.action)


@pytest.mark.django_db
class TestOnboarding:
    def test_onboard_creates_business_owner_subscription(self):
        result = onboard_business(
            business_name="New Business",
            owner_username="newowner",
            owner_email="newowner@test.com",
            owner_password="strongpass123",
        )

        assert result["business"] is not None
        assert result["owner"] is not None
        assert result["subscription"] is not None
        assert result["owner"].role == UserRole.OWNER
        assert result["subscription"].plan == PlanType.FREE

    def test_onboard_validates_business_name(self):
        with pytest.raises(OnboardingError):
            onboard_business(
                business_name="A",
                owner_username="owner",
                owner_email="owner@test.com",
                owner_password="strongpass123",
            )


@pytest.mark.django_db
class TestLimitChecks:
    def test_check_staff_limit_free_plan(self, business, subscription):
        user = create_user(
            business=business,
            username="staff1",
            email="staff1@test.com",
            password="test123",
            role=UserRole.STAFF,
        )
        create_staff(business, user)

        assert check_staff_limit(business) is False

        user2 = create_user(
            business=business,
            username="staff2",
            email="staff2@test.com",
            password="test123",
            role=UserRole.STAFF,
        )
        create_staff(business, user2)

        assert check_staff_limit(business) is False

    def test_check_services_limit(self, business, subscription):
        create_service(business, "Service 1", 30)
        create_service(business, "Service 2", 30)
        create_service(business, "Service 3", 30)

        assert check_services_limit(business) is False

        create_service(business, "Service 4", 30)

        assert check_services_limit(business) is False
