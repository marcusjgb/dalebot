from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["id", "business", "appointment", "notification_type", "status", "scheduled_for"]
    list_filter = ["business", "notification_type", "status"]
