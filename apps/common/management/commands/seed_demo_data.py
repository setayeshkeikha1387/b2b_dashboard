"""Seeds the database with realistic demo data.

Run with `python manage.py seed_demo_data` right after migrating, so a
new team can click around a populated dashboard on day one instead of
staring at empty lists. Safe to re-run — it checks for existing records
by natural key (email, code, title) before creating anything.
"""
from __future__ import annotations

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import User
from apps.core.models import BusinessUnit, Committee, Function
from apps.grc.models import Control, Risk
from apps.tasks.models import Task


class Command(BaseCommand):
    help = "Seed the database with demo Business Units, Risks, Controls, and Tasks."

    def handle(self, *args, **options):
        admin = self._get_or_create_user(
            "admin@example.com", "Ada", "Admin", User.Role.ADMIN, is_staff=True, is_superuser=True,
        )
        manager = self._get_or_create_user("manager@example.com", "Mona", "Manager", User.Role.MANAGER)
        member = self._get_or_create_user("member@example.com", "Milo", "Member", User.Role.MEMBER)

        finance, _ = BusinessUnit.objects.get_or_create(
            code="FIN", defaults={"name": "Finance", "head": manager},
        )
        it, _ = BusinessUnit.objects.get_or_create(
            code="IT", defaults={"name": "Information Technology", "head": manager},
        )

        Function.objects.get_or_create(name="Accounts Payable", business_unit=finance)
        Function.objects.get_or_create(name="IT Security", business_unit=it)

        Committee.objects.get_or_create(
            name="Risk Committee",
            defaults={"business_unit": finance, "chair": admin},
        )

        risk, _ = Risk.objects.get_or_create(
            title="Unpatched production servers",
            defaults={
                "description": "Several production servers are missing critical security patches.",
                "business_unit": it,
                "owner": manager,
                "severity": Risk.Severity.HIGH,
                "likelihood": Risk.Likelihood.LIKELY,
                "status": Risk.Status.OPEN,
            },
        )

        Control.objects.get_or_create(
            title="Monthly patch review",
            risk=risk,
            defaults={
                "description": "IT reviews and applies outstanding OS/security patches monthly.",
                "owner": manager,
                "control_type": Control.ControlType.PREVENTIVE,
                "effectiveness": Control.Effectiveness.PARTIALLY_EFFECTIVE,
            },
        )

        Task.objects.get_or_create(
            title="Patch web-01 and web-02",
            owner=member,
            defaults={
                "description": "Apply the pending security patches flagged in the last scan.",
                "due_date": timezone.localdate() + timedelta(days=3),
                "priority": Task.Priority.HIGH,
                "related_risk": risk,
            },
        )

        self.stdout.write(self.style.SUCCESS(
            "Demo data ready. Log in as admin@example.com / manager@example.com / "
            "member@example.com (password: DemoPass123!) to explore."
        ))

    @staticmethod
    def _get_or_create_user(email: str, first_name: str, last_name: str, role: str, **extra) -> User:
        user, created = User.objects.get_or_create(
            email=email,
            defaults={"first_name": first_name, "last_name": last_name, "role": role, **extra},
        )
        if created:
            user.set_password("DemoPass123!")
            user.save(update_fields=["password"])
        return user
