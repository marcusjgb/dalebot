from django.contrib import admin

from .models import Conversation, Message


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ["id", "business", "customer", "status", "created_at", "updated_at"]
    list_filter = ["business", "status"]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ["id", "conversation", "direction", "timestamp"]
    list_filter = ["direction"]
