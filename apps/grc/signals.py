"""Signal handlers for the grc app.

Notifying the risk owner on creation is done via a signal (rather than
inline in `RiskCreateView.form_valid`, as `apps.tasks` does) so it also
fires for risks created any other way — the Django admin, a data import,
a future API — without every entry point having to remember to call
`notify()` itself.
"""
from __future__ import annotations

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.grc.models import Risk
from apps.notifications.services import notify


@receiver(post_save, sender=Risk)
def notify_owner_of_new_risk(sender, instance: Risk, created: bool, **kwargs) -> None:
    if not created:
        return
    notify(
        recipient=instance.owner,
        message=f"You were assigned as owner of risk: '{instance.title}'.",
        link=instance.get_absolute_url(),
    )
