from django.contrib import admin

from .models import Staff


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ["user", "business", "is_active", "created_at"]
    list_filter = ["business", "is_active"]
    search_fields = ["user__username", "user__first_name", "user__last_name", "business__name"]
    filter_horizontal = ["services"]
