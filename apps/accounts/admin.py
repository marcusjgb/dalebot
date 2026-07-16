from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["username", "email", "business", "role", "is_staff", "is_active"]
    list_filter = ["role", "is_staff", "is_superuser", "business"]
    search_fields = ["username", "email", "first_name", "last_name"]

    fieldsets = BaseUserAdmin.fieldsets + (
        ("Business", {"fields": ("business", "role")}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Business", {"fields": ("business", "role")}),
    )
