from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("apps.accounts.urls")),
    path("notifications/", include("apps.notifications.urls")),
    path("tasks/", include("apps.tasks.urls")),
    path("grc/", include("apps.grc.urls")),
    path("", include("apps.core.urls")),
]
