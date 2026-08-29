"""Makes the unread-notifications badge available in the navbar on every
page without every view having to remember to pass it in."""
from django.http import HttpRequest


def unread_notifications(request: HttpRequest) -> dict:
    if not request.user.is_authenticated:
        return {"unread_notification_count": 0}
    return {"unread_notification_count": request.user.notifications.filter(is_read=False).count()}
