from django.db import models

class ContactInquiry(models.Model):
    CATEGORY_CHOICES = [
        ('general', 'General Inquiry'),
        ('room', 'Room Booking Inquiry'),
        ('event', 'Event & Banquets Inquiry'),
        ('dining', 'Dining & Table Booking'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Contact Inquiry"
        verbose_name_plural = "Contact Inquiries"

    def __str__(self):
        return f"{self.name} - {self.subject} ({self.get_category_display()})"
