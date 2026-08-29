"""Risk and Control models — the core GRC (Governance, Risk & Compliance)
domain of the dashboard."""
from __future__ import annotations

from django.conf import settings
from django.db import models
from django.urls import reverse

from apps.common.models import TimeStampedModel
from apps.core.models import BusinessUnit, Function


class Risk(TimeStampedModel):
    class Severity(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    class Likelihood(models.TextChoices):
        RARE = "rare", "Rare"
        UNLIKELY = "unlikely", "Unlikely"
        POSSIBLE = "possible", "Possible"
        LIKELY = "likely", "Likely"
        ALMOST_CERTAIN = "almost_certain", "Almost certain"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        MITIGATING = "mitigating", "Mitigating"
        CLOSED = "closed", "Closed"

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    business_unit = models.ForeignKey(BusinessUnit, on_delete=models.PROTECT, related_name="risks")
    function = models.ForeignKey(
        Function, null=True, blank=True, on_delete=models.SET_NULL, related_name="risks",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="owned_risks",
    )
    severity = models.CharField(max_length=16, choices=Severity.choices, default=Severity.MEDIUM)
    likelihood = models.CharField(max_length=16, choices=Likelihood.choices, default=Likelihood.POSSIBLE)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.OPEN, db_index=True)

    class Meta(TimeStampedModel.Meta):
        indexes = [models.Index(fields=["status", "severity"])]
        verbose_name = "Risk"

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return reverse("grc:risk_detail", args=[self.pk])

    @property
    def risk_score(self) -> int:
        """A simple 1-5 x 1-5 heat-map score, used for sorting/highlighting
        in the risk register without needing a separate scoring model."""
        severity_weight = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        likelihood_weight = {
            "rare": 1, "unlikely": 2, "possible": 3, "likely": 4, "almost_certain": 5,
        }
        return severity_weight.get(self.severity, 0) * likelihood_weight.get(self.likelihood, 0)


class Control(TimeStampedModel):
    class ControlType(models.TextChoices):
        PREVENTIVE = "preventive", "Preventive"
        DETECTIVE = "detective", "Detective"
        CORRECTIVE = "corrective", "Corrective"

    class Effectiveness(models.TextChoices):
        EFFECTIVE = "effective", "Effective"
        PARTIALLY_EFFECTIVE = "partially_effective", "Partially effective"
        INEFFECTIVE = "ineffective", "Ineffective"
        NOT_TESTED = "not_tested", "Not tested"

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    risk = models.ForeignKey(Risk, on_delete=models.CASCADE, related_name="controls")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="owned_controls",
    )
    control_type = models.CharField(max_length=16, choices=ControlType.choices, default=ControlType.PREVENTIVE)
    effectiveness = models.CharField(
        max_length=24, choices=Effectiveness.choices, default=Effectiveness.NOT_TESTED,
    )
    last_tested_at = models.DateField(null=True, blank=True)

    class Meta(TimeStampedModel.Meta):
        verbose_name = "Control"

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return reverse("grc:control_detail", args=[self.pk])
