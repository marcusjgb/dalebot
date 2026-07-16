from django.contrib import admin

from .models import DailyMetrics


@admin.register(DailyMetrics)
class DailyMetricsAdmin(admin.ModelAdmin):
    list_display = [
        "business",
        "date",
        "total_appointments",
        "confirmed_appointments",
        "cancelled_appointments",
    ]
    list_filter = ["business", "date"]
    date_hierarchy = "date"
