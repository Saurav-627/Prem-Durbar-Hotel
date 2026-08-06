import datetime
import json
from decimal import Decimal

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from rooms.models.room import Room

from ..models.booking import Booking


@csrf_exempt
@require_POST
def channel_manager_sync(request):
    """
    Mock endpoint to sync bookings with channel managers like Booking.com, Expedia, etc.
    Exposes setup hooks for reservation delivery (OTA_HotelResNotifRQ / JSON Webhooks).
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
    except ValueError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    
    # Required channel manager payload parameters
    ota_id = data.get('ota_reservation_id')
    channel = data.get('channel_name', 'OTA-Sync')
    room_id = data.get('room_id')
    check_in_str = data.get('check_in')
    check_out_str = data.get('check_out')
    guest_name = data.get('guest_name')
    guest_email = data.get('guest_email', '')
    guest_phone = data.get('guest_phone', '')
    
    if not all([ota_id, room_id, check_in_str, check_out_str, guest_name]):
        return JsonResponse({'status': 'error', 'message': 'Missing required fields'}, status=400)
        
    try:
        room = Room.objects.prefetch_related('base_prices').get(id=room_id)
    except Room.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Room not found'}, status=404)
        
    try:
        check_in = datetime.date.fromisoformat(check_in_str)
        check_out = datetime.date.fromisoformat(check_out_str)
    except ValueError:
        return JsonResponse({'status': 'error', 'message': 'Invalid dates'}, status=400)
        
    # Check if booking already exists for this OTA reservation
    booking = Booking.objects.filter(ota_reservation_id=ota_id, channel_name=channel).first()
    
    # Calculate price
    nights = (check_out - check_in).days
    subtotal = (room.base_price or Decimal("0.00")) * nights
    total = subtotal
    
    if not booking:
        # Create new OTA Booking
        booking = Booking.objects.create(
            room=room,
            guest_name=guest_name,
            guest_email=guest_email,
            guest_phone=guest_phone,
            check_in=check_in,
            check_out=check_out,
            subtotal=subtotal,
            tax=Decimal("0.00"),
            total=total,
            status='confirmed',  # OTA bookings are usually confirmed
            channel_name=channel,
            ota_reservation_id=ota_id,
            channel_raw_payload=data
        )
        
        return JsonResponse({'status': 'success', 'message': 'Booking created successfully', 'booking_id': booking.id})
    else:
        # Update existing booking details/dates
        booking.guest_name = guest_name
        booking.guest_email = guest_email
        booking.guest_phone = guest_phone
        booking.check_in = check_in
        booking.check_out = check_out
        booking.subtotal = subtotal
        booking.tax = Decimal("0.00")
        booking.total = total
        booking.channel_raw_payload = data
        booking.save()
        
        return JsonResponse({'status': 'success', 'message': 'Booking updated successfully', 'booking_id': booking.id})
