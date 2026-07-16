from django.contrib import admin

from .models import WhatsAppBusinessAccount, WhatsAppEvent


@admin.register(WhatsAppEvent)
class WhatsAppEventAdmin(admin.ModelAdmin):
    list_display = ["event_id", "business", "event_type", "processed", "created_at"]
    list_filter = ["business", "event_type", "processed"]


@admin.register(WhatsAppBusinessAccount)
class WhatsAppBusinessAccountAdmin(admin.ModelAdmin):
    list_display = ["business", "phone_number", "verified_name", "is_active"]
    list_filter = ["is_active"]
