from django.contrib import admin

from .models import Invoice


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ["id", "business", "amount", "status", "period_start", "period_end"]
    list_filter = ["status", "business"]
