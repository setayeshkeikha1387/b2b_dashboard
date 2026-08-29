from django.contrib import admin

from apps.grc.models import Control, Risk


@admin.register(Risk)
class RiskAdmin(admin.ModelAdmin):
    list_display = ["title", "business_unit", "severity", "likelihood", "status", "owner", "risk_score"]
    list_filter = ["status", "severity", "likelihood", "business_unit"]
    search_fields = ["title", "description"]
    autocomplete_fields = ["business_unit", "function", "owner"]

    @admin.display(description="Score")
    def risk_score(self, obj: Risk) -> int:
        return obj.risk_score


@admin.register(Control)
class ControlAdmin(admin.ModelAdmin):
    list_display = ["title", "risk", "control_type", "effectiveness", "owner", "last_tested_at"]
    list_filter = ["control_type", "effectiveness"]
    search_fields = ["title", "description"]
    autocomplete_fields = ["risk", "owner"]
