from django.contrib import admin

from apps.core.models import BusinessUnit, Committee, Function


@admin.register(BusinessUnit)
class BusinessUnitAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "head"]
    search_fields = ["code", "name"]
    autocomplete_fields = ["head"]


@admin.register(Function)
class FunctionAdmin(admin.ModelAdmin):
    list_display = ["name", "business_unit"]
    list_filter = ["business_unit"]
    search_fields = ["name"]
    autocomplete_fields = ["business_unit"]


@admin.register(Committee)
class CommitteeAdmin(admin.ModelAdmin):
    list_display = ["name", "business_unit", "chair"]
    search_fields = ["name"]
    autocomplete_fields = ["business_unit", "chair"]
    filter_horizontal = ["members"]
