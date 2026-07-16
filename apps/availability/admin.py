from django.contrib import admin

from .models import AvailabilityException, AvailabilitySlot


@admin.register(AvailabilitySlot)
class AvailabilitySlotAdmin(admin.ModelAdmin):
    list_display = ["business", "staff", "day_of_week", "start_time", "end_time", "is_active"]
    list_filter = ["business", "day_of_week", "is_active"]


@admin.register(AvailabilityException)
class AvailabilityExceptionAdmin(admin.ModelAdmin):
    list_display = ["business", "staff", "date", "is_available", "reason"]
    list_filter = ["business", "date", "is_available"]
