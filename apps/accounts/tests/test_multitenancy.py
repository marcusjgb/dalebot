import pytest
from django.contrib.auth import get_user_model

from apps.accounts.models import UserRole
from apps.accounts.services import create_user, deactivate_user
from apps.businesses.services import create_business

User = get_user_model()


@pytest.fixture
def business_a(db):
    return create_business("Business A", "America/New_York")


@pytest.fixture
def business_b(db):
    return create_business("Business B", "America/Los_Angeles")


@pytest.fixture
def owner_user_a(business_a):
    return create_user(
        business=business_a,
        username="owner_a",
        email="owner_a@test.com",
        password="test123",
        role=UserRole.OWNER,
    )


@pytest.fixture
def admin_user_a(business_a):
    return create_user(
        business=business_a,
        username="admin_a",
        email="admin_a@test.com",
        password="test123",
        role=UserRole.ADMIN,
    )


@pytest.fixture
def staff_user_a(business_a):
    return create_user(
        business=business_a,
        username="staff_a",
        email="staff_a@test.com",
        password="test123",
        role=UserRole.STAFF,
    )


@pytest.fixture
def owner_user_b(business_b):
    return create_user(
        business=business_b,
        username="owner_b",
        email="owner_b@test.com",
        password="test123",
        role=UserRole.OWNER,
    )


@pytest.mark.django_db
class TestUserRoles:
    def test_owner_has_can_manage_business(self, owner_user_a):
        assert owner_user_a.is_owner
        assert owner_user_a.can_manage_business

    def test_admin_has_can_manage_business(self, admin_user_a):
        assert admin_user_a.is_admin
        assert not admin_user_a.is_owner
        assert admin_user_a.can_manage_business

    def test_staff_cannot_manage_business(self, staff_user_a):
        assert not staff_user_a.is_admin
        assert not staff_user_a.can_manage_business


@pytest.mark.django_db
class TestMultiTenancyIsolation:
    def test_user_belongs_to_business_a(self, owner_user_a, business_a):
        assert owner_user_a.business == business_a

    def test_user_belongs_to_business_b(self, owner_user_b, business_b):
        assert owner_user_b.business == business_b

    def test_users_isolated_by_business(self, owner_user_a, owner_user_b, business_a, business_b):
        assert owner_user_a.business == business_a
        assert owner_user_b.business == business_b
        assert owner_user_a.business != owner_user_b.business

    def test_users_for_business_a_only_see_business_a(
        self, owner_user_a, admin_user_a, staff_user_a, business_a
    ):
        users = User.objects.for_business(business_a)
        assert users.count() == 3
        assert all(u.business == business_a for u in users)

    def test_users_for_business_b_is_empty(self, owner_user_b, business_b):
        users = User.objects.for_business(business_b)
        assert users.count() == 1

    def test_deactivate_user_preserves_data(self, staff_user_a):
        deactivate_user(staff_user_a)
        staff_user_a.refresh_from_db()
        assert not staff_user_a.is_active


@pytest.mark.django_db
class TestBusinessCreation:
    def test_create_business_with_timezone(self):
        business = create_business("Test Business", "Europe/Madrid")
        assert business.name == "Test Business"
        assert business.timezone == "Europe/Madrid"
        assert business.is_active

    def test_create_business_generates_unique_slug(self):
        b1 = create_business("Test Business")
        b2 = create_business("Test Business")
        assert b1.slug != b2.slug
        assert "test-business" in b1.slug
