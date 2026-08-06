import datetime
import uuid
from django.conf import settings
from django.db import models
from django.db.models import Sum
from rooms.models.room_availability import RoomAvailability


class Booking(models.Model):
    # Type hints for Pyrefly IDE static analyzer (Django dynamic DB fields & relations)
    user_id: int | None
    room_id: int | None
    zipline_package_id: int | None
    coupon_id: int | None
    room_dates: models.QuerySet
    # Type hints for Pyrefly IDE static analyzer (Django dynamic DB fields & relations)
    BOOKING_TYPES = (
        ('room', 'Room Booking'),
        ('zipline', 'Zipline Package'),
    )

    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('pending', 'Pending Payment'),
        ('confirmed', 'Confirmed'),
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out'),
        ('cancelled', 'Cancelled'),
    )

    booking_uid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    booking_type = models.CharField(max_length=20, choices=BOOKING_TYPES, default='room')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    room = models.ForeignKey('rooms.Room', on_delete=models.CASCADE, null=True, blank=True, related_name='bookings')
    zipline_package = models.ForeignKey('homepage.ZiplinePackage', on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    
    # Guest details
    guest_name = models.CharField(max_length=150)
    guest_email = models.EmailField()
    guest_phone = models.CharField(max_length=20)
    
    # Room Booking Dates & Guests
    check_in = models.DateField(null=True, blank=True)
    check_out = models.DateField(null=True, blank=True)
    adults = models.IntegerField(default=2)
    children = models.IntegerField(default=0)
    num_rooms = models.PositiveIntegerField(default=1, help_text="Number of rooms booked")

    # Zipline Package Fields
    num_tickets = models.PositiveIntegerField(default=1, help_text="Number of zipline flights / people")
    flight_date = models.DateField(null=True, blank=True, help_text="Date for Zipline flight")
    slot_time = models.CharField(max_length=50, blank=True, null=True, help_text="Preferred time slot e.g. 10:00 AM")
    
    # Liability Waiver Consent Proof
    waiver_accepted = models.BooleanField(default=False, help_text="Whether guest agreed to NAGARKOT ZIPLINE PVT. LTD Waiver & Release of Liability Form")
    waiver_accepted_at = models.DateTimeField(null=True, blank=True, help_text="Timestamp when waiver consent was given")
    
    # Pricing fields
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    currency_code = models.CharField(max_length=10, default='USD', help_text="Currency ISO code used when booking was created")
    coupon = models.ForeignKey('Coupon', on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    special_requests = models.TextField(blank=True, null=True)

    # Channel Manager / OTA Sync Fields (Setup Only)
    channel_name = models.CharField(max_length=50, default='direct', help_text="e.g. direct, booking.com, expedia, agoda")
    ota_reservation_id = models.CharField(max_length=100, blank=True, null=True, help_text="Reservation ID from the OTA/channel manager")
    promo_code = models.CharField(max_length=50, blank=True, null=True)
    payment_method = models.CharField(max_length=50, default='pay_later', choices=[('card', 'Visa/Mastercard'), ('pay_later', 'Pay at Hotel')])
    channel_raw_payload = models.JSONField(blank=True, null=True, help_text="Raw payload received from the channel manager/OTA API")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        if self.booking_type == 'zipline' and self.zipline_package:
            return f"Zipline Booking {self.booking_uid} - {self.guest_name} ({self.zipline_package.name})"
        elif self.room:
            return f"Booking {self.booking_uid} - {self.guest_name} ({self.room.title})"
        return f"Booking {self.booking_uid} - {self.guest_name}"

    @property
    def is_reserved(self):
        return self.status in {'confirmed', 'checked_in', 'checked_out'}

    @property
    def nights(self):
        if self.check_in and self.check_out:
            return (self.check_out - self.check_in).days
        return 0

    @property
    def daily_rate(self):
        n = self.nights
        if n > 0 and self.num_rooms > 0:
            return self.subtotal / (n * self.num_rooms)
        return self.subtotal

    @property
    def per_person_rate(self):
        if self.booking_type == 'zipline' or self.zipline_package_id:
            if self.num_tickets and self.num_tickets > 0:
                return self.subtotal / self.num_tickets
            return self.subtotal
        return self.daily_rate

    @property
    def active_seasonal_price(self):
        """Returns the active RoomSeasonalPrice override if one applies to this booking's dates/currency."""
        if not self.room or not self.check_in or not self.check_out:
            return None
        return (
            self.room.seasonal_prices.filter(
                start_date__lte=self.check_out,
                end_date__gte=self.check_in,
                is_active=True,
                currency__iso_code=self.currency_code
            ).order_by('-start_date').first()
            or self.room.seasonal_prices.filter(
                start_date__lte=self.check_out,
                end_date__gte=self.check_in,
                is_active=True,
                currency__isnull=True
            ).order_by('-start_date').first()
        )

    def has_room_availability(self):
        if self.booking_type == 'zipline' or not self.room or not self.check_in or not self.check_out:
            return True
        check_date = self.check_in
        while check_date < self.check_out:
            booked_count = RoomAvailability.objects.filter(room__category=self.room.category, date=check_date).aggregate(
                total=Sum('rooms_booked')
            )['total'] or 0
            if booked_count + self.num_rooms > self.room.total_rooms:
                return False
            check_date += datetime.timedelta(days=1)
        return True

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        if self.booking_type == 'room' and self.room and self.check_in and self.check_out:
            if self.is_reserved:
                # Delete and recreate so each booking-night is represented once with its room count.
                self.room_dates.all().delete()
                current_date = self.check_in
                while current_date < self.check_out:
                    RoomAvailability.objects.create(
                        room=self.room,
                        date=current_date,
                        rooms_booked=self.num_rooms,
                        is_available=False,
                        booking=self,
                    )
                    current_date += datetime.timedelta(days=1)
            else:
                self.room_dates.all().delete()
        elif hasattr(self, 'room_dates'):
            self.room_dates.all().delete()

    @property
    def status_label(self):
        if self.booking_type == 'zipline' or self.zipline_package_id:
            if self.status == 'checked_in':
                return 'Ticket Redeemed'
            elif self.status == 'checked_out':
                return 'Flight Completed'
            elif self.status == 'confirmed':
                return 'Confirmed'
            elif self.status == 'pending':
                return 'Pending'
            elif self.status == 'cancelled':
                return 'Cancelled'
            elif self.status == 'draft':
                return 'Draft'
        return self.get_status_display()

    # pyrefly: ignore [bad-override]
    def delete(self, *args, **kwargs):
        if hasattr(self, 'room_dates'):
            self.room_dates.all().delete()
        super().delete(*args, **kwargs)
