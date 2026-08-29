from django import forms

from apps.core.models import BusinessUnit, Committee, Function


class BusinessUnitForm(forms.ModelForm):
    class Meta:
        model = BusinessUnit
        fields = ["name", "code", "description", "head"]


class FunctionForm(forms.ModelForm):
    class Meta:
        model = Function
        fields = ["name", "business_unit", "description"]


class CommitteeForm(forms.ModelForm):
    class Meta:
        model = Committee
        fields = ["name", "description", "business_unit", "chair", "members"]
        widgets = {"members": forms.CheckboxSelectMultiple}
