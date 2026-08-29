from django import forms

from apps.grc.models import Control, Risk


class RiskForm(forms.ModelForm):
    class Meta:
        model = Risk
        fields = [
            "title", "description", "business_unit", "function",
            "owner", "severity", "likelihood", "status",
        ]
        widgets = {"description": forms.Textarea(attrs={"rows": 4})}


class ControlForm(forms.ModelForm):
    class Meta:
        model = Control
        fields = [
            "title", "description", "risk", "owner",
            "control_type", "effectiveness", "last_tested_at",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "last_tested_at": forms.DateInput(attrs={"type": "date"}),
        }
