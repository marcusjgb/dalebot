from django.contrib import admin

from .models import Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ["name", "business", "duration_minutes", "price", "is_active"]
    list_filter = ["business", "is_active"]
    search_fields = ["name", "business__name"]
