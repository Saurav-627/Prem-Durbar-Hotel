from django.db import models

class RoomPolicy(models.Model):
    room = models.ForeignKey('Room', on_delete=models.CASCADE, related_name='policies')
    title = models.CharField(max_length=150, help_text="e.g. Cancellation Policy, Pet Policy, Check-in rules")
    description = models.TextField()

    class Meta:
        verbose_name = "Room Policy"
        verbose_name_plural = "Room Policies"

    def __str__(self):
        return f"{self.title} for {self.room.title}"
