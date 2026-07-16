from .models import Customer


def get_customer_by_id(customer_id):
    return Customer.objects.get(id=customer_id)


def get_customers_for_business(business):
    return Customer.objects.filter(business=business, is_active=True).order_by("name")


def get_customer_by_phone(business, phone):
    return Customer.objects.get(business=business, phone=phone)
