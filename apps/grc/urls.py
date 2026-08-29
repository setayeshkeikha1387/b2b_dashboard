from django.urls import path

from apps.grc import views

app_name = "grc"

urlpatterns = [
    path("risks/", views.RiskListView.as_view(), name="risk_list"),
    path("risks/new/", views.RiskCreateView.as_view(), name="risk_create"),
    path("risks/<int:pk>/", views.RiskDetailView.as_view(), name="risk_detail"),
    path("risks/<int:pk>/edit/", views.RiskUpdateView.as_view(), name="risk_update"),
    path("risks/<int:pk>/delete/", views.RiskDeleteView.as_view(), name="risk_delete"),

    path("controls/", views.ControlListView.as_view(), name="control_list"),
    path("controls/new/", views.ControlCreateView.as_view(), name="control_create"),
    path("controls/<int:pk>/", views.ControlDetailView.as_view(), name="control_detail"),
    path("controls/<int:pk>/edit/", views.ControlUpdateView.as_view(), name="control_update"),
    path("controls/<int:pk>/delete/", views.ControlDeleteView.as_view(), name="control_delete"),
]
