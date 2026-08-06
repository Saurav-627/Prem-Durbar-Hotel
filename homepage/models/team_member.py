from django.db import models

from core.utils import UploadTo, ValidateFileSize


class TeamMember(models.Model):
    name = models.CharField(max_length=150)
    role = models.CharField(max_length=150)
    bio = models.TextField(blank=True)
    image = models.ImageField(upload_to=UploadTo('team/members'), blank=True, null=True, validators=[ValidateFileSize(2)])
    order = models.PositiveIntegerField(default=0, help_text="Order of appearance on About Us page")
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ('order', 'id',)
        verbose_name = "Team Member"
        verbose_name_plural = "Team Members"

    def __str__(self):
        return f"{self.name} - {self.role}"

    @property
    def display_image(self):
        if self.image:
            return self.image.url
        role_lower = (self.role or '').lower()
        if 'zipline' in role_lower or 'adventure' in role_lower or 'instructor' in role_lower or 'flight' in role_lower:
            return 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?q=80&w=800&auto=format&fit=crop'
        elif 'chef' in role_lower or 'culinary' in role_lower or 'dining' in role_lower:
            return 'https://images.unsplash.com/photo-1583394838336-acd977736f90?q=80&w=800&auto=format&fit=crop'
        return 'https://images.unsplash.com/photo-1560250097-0b93528c311a?q=80&w=800&auto=format&fit=crop'
