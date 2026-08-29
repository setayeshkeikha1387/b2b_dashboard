import pytest
from django.core import mail
from django.urls import reverse

from apps.notifications.models import Notification
from apps.notifications.services import notify

pytestmark = pytest.mark.django_db


class TestNotifyService:
    def test_notify_creates_notification_and_sends_email(self, member_user):
        notification = notify(recipient=member_user, message="Hello there", link="/tasks/1/")

        assert notification.recipient == member_user
        assert notification.message == "Hello there"
        assert notification.emailed is True
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == [member_user.email]

    def test_notify_with_send_email_false_skips_email(self, member_user):
        notify(recipient=member_user, message="Silent one", send_email=False)
        assert len(mail.outbox) == 0
        assert Notification.objects.filter(message="Silent one").exists()

    def test_notify_swallows_email_failures(self, member_user, monkeypatch):
        def _boom(*args, **kwargs):
            raise RuntimeError("SMTP is down")

        monkeypatch.setattr("apps.notifications.services.send_mail", _boom)

        # Must not raise, even though the email backend blew up.
        notification = notify(recipient=member_user, message="Still created")
        assert notification.pk is not None
        assert notification.emailed is False


class TestNotificationViews:
    def test_list_shows_only_own_notifications(self, logged_in_client, member_user, manager_user):
        mine = Notification.objects.create(recipient=member_user, message="Mine")
        Notification.objects.create(recipient=manager_user, message="Not mine")

        response = logged_in_client.get(reverse("notifications:list"))
        notifications = list(response.context["notifications"])
        assert mine in notifications
        assert len(notifications) == 1

    def test_open_marks_read_and_redirects_to_link(self, logged_in_client, member_user):
        notification = Notification.objects.create(
            recipient=member_user, message="Click me", link="/tasks/",
        )
        response = logged_in_client.get(reverse("notifications:open", args=[notification.pk]))
        assert response.status_code == 302
        assert response.url == "/tasks/"
        notification.refresh_from_db()
        assert notification.is_read is True

    def test_mark_all_read(self, logged_in_client, member_user):
        Notification.objects.create(recipient=member_user, message="One")
        Notification.objects.create(recipient=member_user, message="Two")

        logged_in_client.post(reverse("notifications:mark_all_read"))
        assert Notification.objects.filter(recipient=member_user, is_read=False).count() == 0
