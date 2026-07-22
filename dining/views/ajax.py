from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from ..models.venue import DiningVenue
from ..models.reservation import DiningReservation
import datetime

@require_POST
def book_table_ajax(request, venue_id):
    venue = get_object_or_404(DiningVenue, id=venue_id, is_published=True)
    
    # Retrieve POST data
    name = request.POST.get('name')
    email = request.POST.get('email')
    phone = request.POST.get('phone')
    date_str = request.POST.get('date')
    time_str = request.POST.get('time')
    guests_str = request.POST.get('guests', '2')
    special_requests = request.POST.get('special_requests', '')

    if not name or not email or not phone or not date_str or not time_str:
        return HttpResponse(
            '<div class="p-4 bg-red-900/50 border border-red-500 text-red-200 rounded-lg">Please fill all required fields.</div>',
            status=400
        )

    try:
        date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        time = datetime.datetime.strptime(time_str, "%H:%M").time()
        guests = int(guests_str)
    except ValueError:
        return HttpResponse(
            '<div class="p-4 bg-red-900/50 border border-red-500 text-red-200 rounded-lg">Invalid date, time, or guest format.</div>',
            status=400
        )

    # Save reservation
    DiningReservation.objects.create(
        venue=venue,
        name=name,
        email=email,
        phone=phone,
        date=date,
        time=time,
        guests=guests,
        special_requests=special_requests
    )

    return HttpResponse(
        f'<div class="p-5 bg-amber-900/40 border border-amber-500/50 text-amber-200 rounded-xl animate__animated animate__fadeIn">'
        f'<h4 class="font-semibold text-lg mb-1">Reservation Submitted</h4>'
        f'<p class="text-sm opacity-90">Thank you, {name}. Your table reservation inquiry for {venue.name} on {date} at {time} ({guests} guests) has been received. Our team will contact you shortly to confirm.</p>'
        f'</div>'
    )
