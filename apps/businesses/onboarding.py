from django.contrib.auth.password_validation import validate_password
from django.db import transaction

from apps.accounts.models import UserRole
from apps.accounts.services import create_user as create_user_account
from apps.businesses.services import create_business
from apps.subscriptions.models import PlanType
from apps.subscriptions.services import create_subscription


class OnboardingError(Exception):
    pass


class BusinessSlugExistsError(OnboardingError):
    pass


class ValidationError(OnboardingError):
    pass


@transaction.atomic
def onboard_business(
    business_name,
    owner_username,
    owner_email,
    owner_password,
    business_timezone="America/Argentina/Buenos_Aires",
):
    try:
        validate_business_data(business_name, owner_username, owner_email, owner_password)
    except ValidationError:
        raise
    except Exception as exc:
        raise ValidationError(f"Validation failed: {exc}") from exc

    try:
        business = create_business(
            name=business_name,
            timezone=business_timezone,
        )
    except Exception as exc:
        raise BusinessSlugExistsError(
            f"Business with name '{business_name}' already exists"
        ) from exc

    try:
        owner = create_user_account(
            business=business,
            username=owner_username,
            email=owner_email,
            password=owner_password,
            role=UserRole.OWNER,
        )
    except Exception as exc:
        raise ValidationError(f"Failed to create owner user: {exc}") from exc

    try:
        subscription = create_subscription(business, plan=PlanType.FREE)
    except Exception as exc:
        raise ValidationError(f"Failed to create subscription: {exc}") from exc

    return {
        "business": business,
        "owner": owner,
        "subscription": subscription,
    }


def validate_business_data(business_name, owner_username, owner_email, owner_password):
    errors = {}

    if not business_name or len(business_name) < 2:
        errors["business_name"] = "El nombre del negocio debe tener al menos 2 caracteres"

    if not owner_username or len(owner_username) < 3:
        errors["owner_username"] = "El nombre de usuario debe tener al menos 3 caracteres"

    if not owner_email or "@" not in owner_email:
        errors["owner_email"] = "Email inválido"

    if owner_password:
        try:
            validate_password(owner_password)
        except Exception as e:
            errors["owner_password"] = str(e)

    if errors:
        raise ValidationError(errors)

    return True
