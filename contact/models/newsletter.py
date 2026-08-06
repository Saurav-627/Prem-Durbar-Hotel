from django.db import models
from django.utils import timezone


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True, help_text="Subscriber email address")
    is_verified = models.BooleanField(default=False, help_text="Email ownership verified via double opt-in")
    is_active = models.BooleanField(default=False, help_text="Active subscriber status")
    verification_token = models.CharField(max_length=64, blank=True, null=True, unique=True, help_text="Token for email verification")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = "Newsletter Subscriber"
        verbose_name_plural = "Newsletter Subscribers"

    def __str__(self):
        return f"{self.email} ({'Verified' if self.is_verified else 'Unverified'})"
