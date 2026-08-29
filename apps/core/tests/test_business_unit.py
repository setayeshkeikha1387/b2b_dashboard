import pytest
from django.urls import reverse

from apps.core.models import BusinessUnit

pytestmark = pytest.mark.django_db


class TestDashboard:
    def test_dashboard_loads_for_authenticated_user(self, logged_in_client):
        response = logged_in_client.get(reverse("core:dashboard"))
        assert response.status_code == 200
        assert "open_risk_count" in response.context


class TestBusinessUnitPermissions:
    def test_member_can_view_list(self, logged_in_client, business_unit):
        response = logged_in_client.get(reverse("core:business_unit_list"))
        assert response.status_code == 200
        assert business_unit in response.context["business_units"]

    def test_member_cannot_create(self, logged_in_client):
        response = logged_in_client.post(
            reverse("core:business_unit_create"),
            {"name": "Ops", "code": "OPS", "description": ""},
        )
        assert response.status_code == 403
        assert not BusinessUnit.objects.filter(code="OPS").exists()

    def test_manager_can_create(self, manager_client):
        response = manager_client.post(
            reverse("core:business_unit_create"),
            {"name": "Operations", "code": "OPS", "description": "Ops team"},
        )
        assert response.status_code == 302
        assert BusinessUnit.objects.filter(code="OPS").exists()

    def test_manager_cannot_delete(self, manager_client, business_unit):
        response = manager_client.post(reverse("core:business_unit_delete", args=[business_unit.pk]))
        assert response.status_code == 403
        assert BusinessUnit.objects.filter(pk=business_unit.pk).exists()

    def test_admin_can_delete(self, admin_client, business_unit):
        response = admin_client.post(reverse("core:business_unit_delete", args=[business_unit.pk]))
        assert response.status_code == 302
        assert not BusinessUnit.objects.filter(pk=business_unit.pk).exists()

    def test_search_filters_by_name_or_code(self, logged_in_client, business_unit):
        response = logged_in_client.get(reverse("core:business_unit_list"), {"q": "FIN"})
        assert business_unit in response.context["business_units"]

        response = logged_in_client.get(reverse("core:business_unit_list"), {"q": "nonexistent"})
        assert business_unit not in response.context["business_units"]
