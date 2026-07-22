from django.db import models

class RoomAvailability(models.Model):
    room = models.ForeignKey('Room', on_delete=models.CASCADE, related_name='availabilities')
    date = models.DateField()
    rooms_booked = models.PositiveIntegerField(default=1, help_text='Number of physical rooms occupied for this booking-night')
    is_available = models.BooleanField(default=True)
    booking = models.ForeignKey('booking.Booking', on_delete=models.SET_NULL, null=True, blank=True, related_name='room_dates')

    class Meta:
        verbose_name = 'Room Occupancy'
        verbose_name_plural = 'Room Occupancies'
        constraints = [
            models.UniqueConstraint(fields=['room', 'date', 'booking'], name='unique_room_booking_day_occupancy'),
        ]

    def __str__(self):
        status = 'Available' if self.is_available else 'Booked'
        if self.booking:
            return f"{self.room.title} on {self.date}: {status} for {self.booking.guest_name} ({self.rooms_booked} room(s))"
        return f"{self.room.title} on {self.date}: {status}"
