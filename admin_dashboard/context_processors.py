from .models.notification import Notification

def admin_notifications(request):
    """
    Context processor providing recent unread notifications and count for the admin dashboard header.
    """
    if request.user.is_authenticated and request.user.is_staff:
        recent_notifications = Notification.objects.all()[:6]
        unread_count = Notification.objects.filter(is_read=False).count()
        return {
            'header_notifications': recent_notifications,
            'unread_notifications_count': unread_count
        }
    return {
        'header_notifications': [],
        'unread_notifications_count': 0
    }
