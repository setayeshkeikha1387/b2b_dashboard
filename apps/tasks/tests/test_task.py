import pytest
from django.urls import reverse
from django.utils import timezone

from apps.notifications.models import Notification
from apps.tasks.models import Task

pytestmark = pytest.mark.django_db


class TestTaskCreation:
    def test_creating_a_task_notifies_the_owner(self, logged_in_client, member_user):
        response = logged_in_client.post(
            reverse("tasks:task_create"),
            {
                "title": "Review Q3 access logs",
                "description": "",
                "owner": member_user.pk,
                "priority": Task.Priority.MEDIUM,
                "status": Task.Status.TODO,
            },
        )
        assert response.status_code == 302
        task = Task.objects.get(title="Review Q3 access logs")
        assert Notification.objects.filter(recipient=member_user, message__icontains=task.title).exists()


class TestMarkDone:
    def test_owner_can_mark_own_task_done(self, logged_in_client, member_user):
        task = Task.objects.create(title="Finish report", owner=member_user)
        response = logged_in_client.post(reverse("tasks:task_mark_done", args=[task.pk]))
        assert response.status_code == 302
        task.refresh_from_db()
        assert task.status == Task.Status.DONE
        assert task.completed_at is not None

    def test_other_member_cannot_mark_someone_elses_task_done(self, client, member_user, admin_user):
        other_user = admin_user.__class__.objects.create_user(
            email="other@example.com", password="StrongPass123!"
        )
        task = Task.objects.create(title="Not yours", owner=member_user)
        client.force_login(other_user)

        response = client.post(reverse("tasks:task_mark_done", args=[task.pk]))
        assert response.status_code == 302  # redirected back with an error message
        task.refresh_from_db()
        assert task.status == Task.Status.TODO

    def test_manager_can_mark_anyones_task_done(self, manager_client, member_user):
        task = Task.objects.create(title="Team task", owner=member_user)
        response = manager_client.post(reverse("tasks:task_mark_done", args=[task.pk]))
        assert response.status_code == 302
        task.refresh_from_db()
        assert task.status == Task.Status.DONE


class TestIsOverdue:
    def test_past_due_incomplete_task_is_overdue(self, member_user):
        task = Task.objects.create(
            title="Late task", owner=member_user,
            due_date=timezone.localdate() - timezone.timedelta(days=1),
        )
        assert task.is_overdue is True

    def test_done_task_is_never_overdue(self, member_user):
        task = Task.objects.create(
            title="Late but done", owner=member_user,
            due_date=timezone.localdate() - timezone.timedelta(days=1),
            status=Task.Status.DONE,
        )
        assert task.is_overdue is False


class TestTaskListFiltering:
    def test_status_filter(self, logged_in_client, member_user):
        Task.objects.create(title="Todo task", owner=member_user, status=Task.Status.TODO)
        Task.objects.create(title="Done task", owner=member_user, status=Task.Status.DONE)

        response = logged_in_client.get(reverse("tasks:task_list"), {"status": "done"})
        titles = [t.title for t in response.context["tasks"]]
        assert "Done task" in titles
        assert "Todo task" not in titles
