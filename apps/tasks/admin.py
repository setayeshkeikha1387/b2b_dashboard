from django.contrib import admin

from apps.tasks.models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ["title", "owner", "status", "priority", "due_date", "is_overdue"]
    list_filter = ["status", "priority"]
    search_fields = ["title", "owner__email"]
    autocomplete_fields = ["owner", "related_risk", "related_control"]
    readonly_fields = ["completed_at", "created_at", "updated_at"]

    @admin.display(boolean=True, description="Overdue")
    def is_overdue(self, obj: Task) -> bool:
        return obj.is_overdue
