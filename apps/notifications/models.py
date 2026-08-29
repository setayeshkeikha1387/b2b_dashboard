"""In-app notifications, optionally mirrored to email.

Deliberately simple (no generic foreign key / content-type machinery):
a notification is just a message + an optional link, which is all an
MVP needs. If the project grows enough to need per-notification-type
templates or user preferences, this model is the natural place to add
a `category` field and branch on it.
"""
from __future__ import annotations

from django.conf import settings
from django.db import models
from django.urls import reverse

from apps.common.models import TimeStampedModel


class Notification(TimeStampedModel):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications",
    )
    message = models.CharField(max_length=255)
    link = models.CharField(
        max_length=255, blank=True,
        help_text="Relative URL the notification should take the user to when clicked.",
    )
    is_read = models.BooleanField(default=False, db_index=True)
    emailed = models.BooleanField(default=False, help_text="Whether this was also sent via email.")

    class Meta(TimeStampedModel.Meta):
        verbose_name = "Notification"

    def __str__(self) -> str:
        return f"{self.message} → {self.recipient}"

    def get_absolute_url(self) -> str:
        return self.link or reverse("notifications:list")
