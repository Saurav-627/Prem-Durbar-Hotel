from django.views.generic import ListView, DetailView
from django.db.models import Sum
from django.http import JsonResponse
from django.views.decorators.http import require_GET
import datetime
from ..models.room import Room
from ..models.room_facility import RoomFacility
from ..models.room_category import RoomCategory
from ..models.room_availability import RoomAvailability

class RoomListView(ListView):
    model = Room
    template_name = 'rooms/room_list.html'
    context_object_name = 'rooms'
    paginate_by = 6

    def get_queryset(self):
        queryset = super().get_queryset().filter(is_published=True)
        
        # Get active currency from cookie, fallback to default published currency or USD
        from settings_manager.models.currency import Currency
        try:
            published_currencies = list(Currency.objects.filter(is_published=True))
            default_currency = 'USD'
            selected_currency = self.request.COOKIES.get('currency', default_currency)
            valid_codes = [c.iso_code for c in published_currencies]
            if selected_currency not in valid_codes:
                selected_currency = default_currency
        except Exception:
            selected_currency = 'USD'

        queryset = queryset.filter(base_prices__currency__iso_code=selected_currency)
        
        # Prefetch the active currency price
        from django.db.models import Prefetch
        from rooms.models.room_base_price import RoomBasePrice
        queryset = queryset.prefetch_related(
            Prefetch(
                'base_prices',
                queryset=RoomBasePrice.objects.filter(currency__iso_code=selected_currency),
                to_attr='active_currency_price'
            ),
            'seasonal_prices__currency',
        )
        
        # Filtering parameters
        category = self.request.GET.get('category')
        adults = self.request.GET.get('adults')
        price_min = self.request.GET.get('price_min')
        price_max = self.request.GET.get('price_max')

        if category:
            queryset = queryset.filter(category__slug=category)
        if adults:
            try:
                queryset = queryset.filter(max_adults__gte=int(adults))
            except ValueError:
                pass
        if price_min:
            try:
                queryset = queryset.filter(base_prices__currency__iso_code=selected_currency, base_prices__base_price__gte=float(price_min))
            except ValueError:
                pass
        if price_max:
            try:
                queryset = queryset.filter(base_prices__currency__iso_code=selected_currency, base_prices__base_price__lte=float(price_max))
            except ValueError:
                pass
                
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = RoomCategory.objects.filter(is_published=True)
        context['facilities'] = RoomFacility.objects.all()
        
        # Resolve active currency symbol
        from settings_manager.models.currency import Currency
        try:
            default_currency = 'USD'
            selected_currency = self.request.COOKIES.get('currency', default_currency)
            currency_obj = Currency.objects.filter(iso_code=selected_currency, is_published=True).first()
            context['selected_currency_symbol'] = currency_obj.symbol if currency_obj else '$'
        except Exception:
            selected_currency = 'USD'
            context['selected_currency_symbol'] = '$'
            
        # Set active currency context on all rooms on the current page
        rooms = context.get('rooms', [])
        for r in rooms:
            r.set_active_currency(selected_currency)
            
        return context

class RoomDetailView(DetailView):
    model = Room
    template_name = 'rooms/room_detail.html'
    context_object_name = 'room'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        selected_currency = self.request.COOKIES.get('currency', 'USD')
        from django.db.models import Prefetch
        from rooms.models.room_base_price import RoomBasePrice
        return super().get_queryset().filter(is_published=True).prefetch_related(
            'images', 'facilities', 'policies', 'seasonal_prices__currency',
            Prefetch(
                'base_prices',
                queryset=RoomBasePrice.objects.filter(currency__iso_code=selected_currency),
                to_attr='active_currency_price'
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        selected_currency = self.request.COOKIES.get('currency', 'USD')
        if self.object:
            self.object.set_active_currency(selected_currency)
        
        # Resolve active currency symbol
        from settings_manager.models.currency import Currency
        try:
            currency_obj = Currency.objects.filter(iso_code=selected_currency, is_published=True).first()
            context['selected_currency_symbol'] = currency_obj.symbol if currency_obj else '$'
        except Exception:
            context['selected_currency_symbol'] = '$'
            
        return context

@require_GET
def check_room_availability(request, room_id):
    check_in_str = request.GET.get('check_in')
    check_out_str = request.GET.get('check_out')
    num_rooms_str = request.GET.get('num_rooms', '1')
    
    if not check_in_str or not check_out_str:
        return JsonResponse({'available': False, 'message': 'Missing date parameters.'}, status=400)
        
    try:
        check_in = datetime.datetime.strptime(check_in_str, "%Y-%m-%d").date()
        check_out = datetime.datetime.strptime(check_out_str, "%Y-%m-%d").date()
        num_rooms = int(num_rooms_str)
    except ValueError:
        return JsonResponse({'available': False, 'message': 'Invalid parameter format.'}, status=400)
        
    if check_out <= check_in:
        return JsonResponse({'available': False, 'message': 'Departure must be after arrival.'}, status=400)
        
    from ..models.room import Room
    try:
        room = Room.objects.get(id=room_id)
    except Room.DoesNotExist:
        return JsonResponse({'available': False, 'message': 'Room not found.'}, status=404)

    is_available = True
    available_rooms = room.total_rooms
    check_date = check_in
    while check_date < check_out:
        booked_count = RoomAvailability.objects.filter(room__category=room.category, date=check_date).aggregate(
            total=Sum('rooms_booked')
        )['total'] or 0
        remaining = room.total_rooms - booked_count
        if remaining < available_rooms:
            available_rooms = remaining
        if booked_count + num_rooms > room.total_rooms:
            is_available = False
        check_date += datetime.timedelta(days=1)
    
    return JsonResponse({
        'available': is_available,
        'available_rooms': max(0, available_rooms),
    })


@require_GET
def get_room_booked_dates(request, room_id):
    try:
        room = Room.objects.get(id=room_id)
    except Room.DoesNotExist:
        return JsonResponse({'booked_dates': []}, status=404)
        
    # Get all occupancies from today onwards
    today = datetime.date.today()
    
    # We aggregate total booked rooms grouped by date
    occupancies = RoomAvailability.objects.filter(
        room__category=room.category,
        date__gte=today
    ).values('date').annotate(total_booked=Sum('rooms_booked'))
    
    booked_dates = []
    for occ in occupancies:
        # If total booked rooms matches or exceeds total rooms of this category
        if occ['total_booked'] >= room.total_rooms:
            booked_dates.append(occ['date'].strftime('%Y-%m-%d'))
            
    return JsonResponse({'booked_dates': booked_dates})


