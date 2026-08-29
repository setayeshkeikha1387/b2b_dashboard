from django.urls import path

from apps.notifications import views

app_name = "notifications"

urlpatterns = [
    path("", views.NotificationListView.as_view(), name="list"),
    path("<int:pk>/open/", views.NotificationOpenView.as_view(), name="open"),
    path("mark-all-read/", views.MarkAllNotificationsReadView.as_view(), name="mark_all_read"),
]
