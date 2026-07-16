from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction

User = get_user_model()


@transaction.atomic
def create_user(
    business,
    username,
    email,
    password=None,
    role="staff",
    first_name="",
    last_name="",
):
    if password:
        validate_password(password)

    user = User.objects.create(
        business=business,
        username=username,
        email=email,
        role=role,
        first_name=first_name,
        last_name=last_name,
    )
    user.set_password(password or username)
    user.save()
    return user


@transaction.atomic
def update_user(user, **kwargs):
    allowed = ["first_name", "last_name", "email", "role", "is_active"]
    for key, value in kwargs.items():
        if key in allowed:
            setattr(user, key, value)

    if "password" in kwargs:
        validate_password(kwargs["password"])
        user.set_password(kwargs["password"])

    user.save()
    return user


@transaction.atomic
def deactivate_user(user):
    user.is_active = False
    user.save()
    return user
