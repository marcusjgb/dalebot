from django.db import transaction


@transaction.atomic
def create_service(business, name, duration_minutes, price=0, description=""):
    from .models import Service
    return Service.objects.create(
        business=business,
        name=name,
        duration_minutes=duration_minutes,
        price=price,
        description=description,
    )


@transaction.atomic
def update_service(service, **kwargs):
    allowed = ["name", "description", "duration_minutes", "price", "is_active"]
    for key, value in kwargs.items():
        if key in allowed:
            setattr(service, key, value)
    service.save()
    return service


@transaction.atomic
def deactivate_service(service):
    service.is_active = False
    service.save()
    return service
