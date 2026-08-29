import pytest
from django.core import mail
from django.urls import reverse

from apps.grc.models import Risk
from apps.notifications.models import Notification

pytestmark = pytest.mark.django_db


class TestRiskCreation:
    def test_manager_can_create_risk(self, manager_client, business_unit, manager_user):
        response = manager_client.post(
            reverse("grc:risk_create"),
            {
                "title": "Vendor concentration risk",
                "description": "Too reliant on a single supplier.",
                "business_unit": business_unit.pk,
                "owner": manager_user.pk,
                "severity": Risk.Severity.HIGH,
                "likelihood": Risk.Likelihood.POSSIBLE,
                "status": Risk.Status.OPEN,
            },
        )
        assert response.status_code == 302
        assert Risk.objects.filter(title="Vendor concentration risk").exists()

    def test_member_cannot_create_risk(self, logged_in_client, business_unit, member_user):
        response = logged_in_client.post(
            reverse("grc:risk_create"),
            {
                "title": "Should not be created",
                "business_unit": business_unit.pk,
                "owner": member_user.pk,
                "severity": Risk.Severity.LOW,
                "likelihood": Risk.Likelihood.RARE,
                "status": Risk.Status.OPEN,
            },
        )
        assert response.status_code == 403
        assert not Risk.objects.filter(title="Should not be created").exists()


class TestRiskCreationNotifiesOwner:
    """Exercises the signal in apps/grc/signals.py end-to-end."""

    def test_creating_a_risk_notifies_and_emails_the_owner(self, business_unit, member_user):
        Risk.objects.create(
            title="Data retention risk",
            business_unit=business_unit,
            owner=member_user,
            severity=Risk.Severity.MEDIUM,
            likelihood=Risk.Likelihood.POSSIBLE,
        )

        notification = Notification.objects.get(recipient=member_user)
        assert "Data retention risk" in notification.message
        assert notification.emailed is True

        assert len(mail.outbox) == 1
        assert member_user.email in mail.outbox[0].to

    def test_updating_an_existing_risk_does_not_renotify(self, business_unit, member_user):
        risk = Risk.objects.create(
            title="Initial title", business_unit=business_unit, owner=member_user,
        )
        assert Notification.objects.filter(recipient=member_user).count() == 1

        risk.title = "Updated title"
        risk.save()

        assert Notification.objects.filter(recipient=member_user).count() == 1


class TestRiskScore:
    def test_risk_score_combines_severity_and_likelihood(self, business_unit, member_user):
        risk = Risk.objects.create(
            title="Scored risk",
            business_unit=business_unit,
            owner=member_user,
            severity=Risk.Severity.HIGH,       # weight 3
            likelihood=Risk.Likelihood.LIKELY,  # weight 4
        )
        assert risk.risk_score == 12
