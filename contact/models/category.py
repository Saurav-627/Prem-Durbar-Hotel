from django.db import models

class ContactInquiryCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    ordering = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['ordering', 'name']
        verbose_name = "Contact Inquiry Category"
        verbose_name_plural = "Contact Inquiry Categories"

    def __str__(self):
        return self.name
