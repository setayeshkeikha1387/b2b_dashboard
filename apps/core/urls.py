from django.urls import path

from apps.core import views

app_name = "core"

urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),

    path("business-units/", views.BusinessUnitListView.as_view(), name="business_unit_list"),
    path("business-units/new/", views.BusinessUnitCreateView.as_view(), name="business_unit_create"),
    path("business-units/<int:pk>/", views.BusinessUnitDetailView.as_view(), name="business_unit_detail"),
    path("business-units/<int:pk>/edit/", views.BusinessUnitUpdateView.as_view(), name="business_unit_update"),
    path("business-units/<int:pk>/delete/", views.BusinessUnitDeleteView.as_view(), name="business_unit_delete"),

    path("functions/", views.FunctionListView.as_view(), name="function_list"),
    path("functions/new/", views.FunctionCreateView.as_view(), name="function_create"),
    path("functions/<int:pk>/", views.FunctionDetailView.as_view(), name="function_detail"),
    path("functions/<int:pk>/edit/", views.FunctionUpdateView.as_view(), name="function_update"),
    path("functions/<int:pk>/delete/", views.FunctionDeleteView.as_view(), name="function_delete"),

    path("committees/", views.CommitteeListView.as_view(), name="committee_list"),
    path("committees/new/", views.CommitteeCreateView.as_view(), name="committee_create"),
    path("committees/<int:pk>/", views.CommitteeDetailView.as_view(), name="committee_detail"),
    path("committees/<int:pk>/edit/", views.CommitteeUpdateView.as_view(), name="committee_update"),
    path("committees/<int:pk>/delete/", views.CommitteeDeleteView.as_view(), name="committee_delete"),
]
