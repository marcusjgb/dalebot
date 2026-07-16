from .models import Business


def get_business_by_id(business_id):
    return Business.objects.get(id=business_id)


def get_business_by_slug(slug):
    return Business.objects.get(slug=slug)


def get_all_businesses():
    return Business.objects.filter(is_active=True).order_by("name")


def get_businesses_for_user(user):
    if user.is_owner or user.is_admin:
        return Business.objects.filter(id=user.business_id)
    return Business.objects.none()
