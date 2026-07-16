from django.db import IntegrityError, transaction
from django.utils.text import slugify


def create_business(name, timezone="America/Argentina/Buenos_Aires"):
    base_slug = slugify(name)
    slug = base_slug
    counter = 1

    while True:
        try:
            from .models import Business
            with transaction.atomic():
                business = Business.objects.create(
                    name=name,
                    slug=slug,
                    timezone=timezone,
                )
            return business
        except IntegrityError:
            counter += 1
            slug = f"{base_slug}-{counter}"


@transaction.atomic
def update_business(business, **kwargs):
    allowed = [
        "name", "timezone", "is_active", "phone", "email", "address", "logo_url",
        "whatsapp_phone_number_id", "whatsapp_verify_token", "whatsapp_access_token",
        "whatsapp_enabled",
    ]
    for key, value in kwargs.items():
        if key in allowed:
            setattr(business, key, value)
    business.save()
    return business
