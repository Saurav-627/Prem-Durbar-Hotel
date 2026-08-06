from django.db import models
from django.utils import timezone


class Notification(models.Model):
    """
    Administrative System Notification Model for real-time staff alerts.
    """
    NOTIFICATION_TYPES = (
        ('booking_created', 'New Booking Placed'),
        ('payment_success', 'Payment Received'),
        ('booking_confirmed', 'Booking Confirmed'),
        ('inquiry_received', 'Contact Inquiry Received'),
    )

    notification_type = models.CharField(
        max_length=30,
        choices=NOTIFICATION_TYPES,
        default='booking_created'
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    link_url = models.CharField(max_length=255, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        return f"[{self.get_notification_type_display()}] {self.title}"


def create_admin_notification(notification_type, title, message, link_url=None):
    """
    Helper function to dispatch an admin notification cleanly from anywhere in the platform.
    """
    try:
        return Notification.objects.create(
            notification_type=notification_type,
            title=title,
            message=message,
            link_url=link_url
        )
    except (ValueError, TypeError, KeyError, AttributeError, RuntimeError, OSError) as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to create admin notification: {e}")
        return None
