"""Notification dispatch service.

`notify()` is the single function every app in the project calls to tell
a user something happened (task assigned, risk created, etc.) — it always
creates the in-app `Notification` row, and optionally emails it too. This
keeps "how do we tell a user something" in one place instead of each app
reinventing email-sending and duplicating the is_read/emailed bookkeeping.
"""
from __future__ import annotations

import logging

from django.conf import settings
from django.core.mail import send_mail

from apps.accounts.models import User
from apps.notifications.models import Notification

logger = logging.getLogger(__name__)


def notify(
    recipient: User,
    message: str,
    link: str = "",
    send_email: bool = True,
) -> Notification:
    """Create an in-app notification for `recipient`, and email it too
    unless `send_email=False`.

    Failures to send email are logged and swallowed rather than raised —
    a broken SMTP configuration should never prevent the triggering
    action (e.g. saving a Task) from completing successfully.
    """
    notification = Notification.objects.create(recipient=recipient, message=message, link=link)

    if send_email and recipient.email:
        absolute_link = f"{settings.SITE_BASE_URL}{link}" if link else settings.SITE_BASE_URL
        try:
            send_mail(
                subject="B2B Dashboard notification",
                message=f"{message}\n\n{absolute_link}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient.email],
                fail_silently=False,
            )
            notification.emailed = True
            notification.save(update_fields=["emailed"])
        except Exception:  # noqa: BLE001 — email failures must never break the caller
            logger.exception("Failed to email notification %s to %s", notification.pk, recipient.email)

    return notification
