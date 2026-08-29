from django.contrib import admin

from apps.notifications.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["message", "recipient", "is_read", "emailed", "created_at"]
    list_filter = ["is_read", "emailed"]
    search_fields = ["message", "recipient__email"]
    readonly_fields = ["created_at", "updated_at"]
