import pytest
from django.urls import reverse

from apps.accounts.models import User

pytestmark = pytest.mark.django_db


class TestSignup:
    def test_signup_creates_member_user_and_logs_in(self, client):
        response = client.post(
            reverse("accounts:signup"),
            {
                "email": "newuser@example.com",
                "first_name": "New",
                "last_name": "User",
                "job_title": "Analyst",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )
        assert response.status_code == 302
        user = User.objects.get(email="newuser@example.com")
        assert user.role == User.Role.MEMBER
        assert user.check_password("StrongPass123!")

        # Signup should also log the user in immediately.
        dashboard_response = client.get(reverse("core:dashboard"))
        assert dashboard_response.status_code == 200

    def test_signup_rejects_duplicate_email(self, client, member_user):
        response = client.post(
            reverse("accounts:signup"),
            {
                "email": member_user.email,
                "first_name": "Dup",
                "last_name": "Licate",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )
        assert response.status_code == 200  # re-renders form with errors
        assert "already exists" in response.content.decode()

    def test_signup_rejects_mismatched_passwords(self, client):
        response = client.post(
            reverse("accounts:signup"),
            {
                "email": "mismatch@example.com",
                "first_name": "A",
                "last_name": "B",
                "password1": "StrongPass123!",
                "password2": "DifferentPass456!",
            },
        )
        assert response.status_code == 200
        assert not User.objects.filter(email="mismatch@example.com").exists()


class TestLogin:
    def test_login_with_correct_credentials(self, client, member_user):
        response = client.post(
            reverse("accounts:login"),
            {"username": member_user.email, "password": "StrongPass123!"},
        )
        assert response.status_code == 302

    def test_login_with_wrong_password_fails(self, client, member_user):
        response = client.post(
            reverse("accounts:login"),
            {"username": member_user.email, "password": "wrong-password"},
        )
        assert response.status_code == 200
        assert response.wsgi_request.user.is_authenticated is False

    def test_dashboard_requires_login(self, client):
        response = client.get(reverse("core:dashboard"))
        assert response.status_code == 302
        assert reverse("accounts:login") in response.url


class TestProfile:
    def test_user_can_update_own_profile(self, logged_in_client, member_user):
        response = logged_in_client.post(
            reverse("accounts:profile"),
            {"first_name": "Updated", "last_name": "Name", "job_title": "Lead Analyst"},
        )
        assert response.status_code == 302
        member_user.refresh_from_db()
        assert member_user.first_name == "Updated"
        assert member_user.job_title == "Lead Analyst"
