from django.contrib import admin

from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ["id", "customer", "service", "staff", "starts_at", "status"]
    list_filter = ["business", "status", "starts_at"]
    search_fields = ["customer__name", "service__name"]
    date_hierarchy = "starts_at"
