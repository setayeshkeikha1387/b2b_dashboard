"""Organizational master data: BusinessUnit, Function, Committee.

These models represent the company's structure and are shared reference
data for the GRC (Risk/Control) and Task modules — every Risk belongs to
a BusinessUnit, Tasks can reference either, etc.
"""
from __future__ import annotations

from django.conf import settings
from django.db import models
from django.urls import reverse

from apps.common.models import TimeStampedModel


class BusinessUnit(TimeStampedModel):
    name = models.CharField(max_length=150, unique=True)
    code = models.CharField(max_length=20, unique=True, help_text="Short internal code, e.g. 'FIN', 'OPS'.")
    description = models.TextField(blank=True)
    head = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="headed_business_units",
    )

    class Meta(TimeStampedModel.Meta):
        ordering = ["name"]
        verbose_name = "Business Unit"

    def __str__(self) -> str:
        return f"{self.code} — {self.name}"

    def get_absolute_url(self) -> str:
        return reverse("core:business_unit_detail", args=[self.pk])


class Function(TimeStampedModel):
    """A functional department/discipline within a BusinessUnit (e.g.
    'Finance Ops', 'IT Security') — the level below BusinessUnit that
    Risks and Controls can optionally be tagged with for finer reporting."""

    name = models.CharField(max_length=150)
    business_unit = models.ForeignKey(BusinessUnit, on_delete=models.CASCADE, related_name="functions")
    description = models.TextField(blank=True)

    class Meta(TimeStampedModel.Meta):
        ordering = ["business_unit__name", "name"]
        unique_together = [("business_unit", "name")]
        verbose_name = "Function"

    def __str__(self) -> str:
        return f"{self.name} ({self.business_unit.code})"

    def get_absolute_url(self) -> str:
        return reverse("core:function_detail", args=[self.pk])


class Committee(TimeStampedModel):
    """A governance body (e.g. 'Risk Committee', 'Audit Committee') that
    oversees risks/controls for one or more business units."""

    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)
    business_unit = models.ForeignKey(
        BusinessUnit, null=True, blank=True, on_delete=models.SET_NULL, related_name="committees",
    )
    chair = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="chaired_committees",
    )
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="committees")

    class Meta(TimeStampedModel.Meta):
        ordering = ["name"]
        verbose_name = "Committee"

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse("core:committee_detail", args=[self.pk])
