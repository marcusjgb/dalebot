from django.db import transaction


@transaction.atomic
def create_customer(business, name, phone, email="", notes=""):
    from .models import Customer
    return Customer.objects.create(
        business=business,
        name=name,
        phone=phone,
        email=email,
        notes=notes,
    )


@transaction.atomic
def update_customer(customer, **kwargs):
    allowed = ["name", "phone", "email", "notes", "is_active"]
    for key, value in kwargs.items():
        if key in allowed:
            setattr(customer, key, value)
    customer.save()
    return customer


@transaction.atomic
def deactivate_customer(customer):
    customer.is_active = False
    customer.save()
    return customer


def get_customer_by_phone(business, phone):
    from .models import Customer
    return Customer.objects.get(business=business, phone=phone)
