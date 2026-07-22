from django.db import models

class Branch(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=50)
    email = models.EmailField()
    maps_iframe = models.TextField(blank=True, null=True, help_text="Google Maps iframe embed code")
    is_main = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True, help_text="Designates whether this branch is visible on the website")

    class Meta:
        verbose_name = "Hotel Branch"
        verbose_name_plural = "Hotel Branches"

    def __str__(self):
        return f"{self.name} ({'Main' if self.is_main else 'Sub-branch'})"
