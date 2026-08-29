from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView

from apps.notifications.models import Notification


class NotificationListView(LoginRequiredMixin, ListView):
    """Every notification for the current user, newest first."""

    model = Notification
    context_object_name = "notifications"
    template_name = "notifications/notification_list.html"
    paginate_by = 30

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)


class NotificationOpenView(LoginRequiredMixin, View):
    """Marks a single notification read, then redirects to its target
    link — this is what the navbar dropdown items point to."""

    def get(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
        if not notification.is_read:
            notification.is_read = True
            notification.save(update_fields=["is_read"])
        return redirect(notification.get_absolute_url())


class MarkAllNotificationsReadView(LoginRequiredMixin, View):
    def post(self, request):
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return redirect(reverse_lazy("notifications:list"))
