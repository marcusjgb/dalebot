from django.contrib.auth import get_user_model

User = get_user_model()


def get_user_by_id(user_id):
    return User.objects.get(id=user_id)


def get_users_for_business(business):
    return User.objects.for_business(business).order_by("username")


def get_active_users_for_business(business):
    return User.objects.for_business(business).active().order_by("username")
