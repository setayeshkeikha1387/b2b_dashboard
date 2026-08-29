import pytest
from django.core.management import call_command

from apps.accounts.models import User
from apps.grc.models import Risk
from apps.tasks.models import Task

pytestmark = pytest.mark.django_db


class TestSeedDemoData:
    def test_seed_creates_expected_records(self):
        call_command("seed_demo_data")

        assert User.objects.filter(email="admin@example.com", role=User.Role.ADMIN).exists()
        assert User.objects.filter(email="manager@example.com", role=User.Role.MANAGER).exists()
        assert User.objects.filter(email="member@example.com", role=User.Role.MEMBER).exists()
        assert Risk.objects.filter(title="Unpatched production servers").exists()
        assert Task.objects.filter(title="Patch web-01 and web-02").exists()

    def test_seed_is_idempotent(self):
        call_command("seed_demo_data")
        call_command("seed_demo_data")

        assert User.objects.filter(email="admin@example.com").count() == 1
        assert Risk.objects.filter(title="Unpatched production servers").count() == 1
