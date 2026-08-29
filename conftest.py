import pytest
from django.test import Client

from apps.accounts.models import User
from apps.core.models import BusinessUnit


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def admin_user(db):
    return User.objects.create_user(
        email="admin@example.com", password="StrongPass123!", role=User.Role.ADMIN, is_staff=True,
    )


@pytest.fixture
def manager_user(db):
    return User.objects.create_user(
        email="manager@example.com", password="StrongPass123!", role=User.Role.MANAGER,
    )


@pytest.fixture
def member_user(db):
    return User.objects.create_user(
        email="member@example.com", password="StrongPass123!", role=User.Role.MEMBER,
    )


@pytest.fixture
def business_unit(db, manager_user):
    return BusinessUnit.objects.create(name="Finance", code="FIN", head=manager_user)


@pytest.fixture
def logged_in_client(client, member_user):
    client.force_login(member_user)
    return client


@pytest.fixture
def manager_client(client, manager_user):
    client.force_login(manager_user)
    return client


@pytest.fixture
def admin_client(client, admin_user):
    client.force_login(admin_user)
    return client
