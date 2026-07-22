import datetime
from decimal import Decimal
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, CreateView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.forms import inlineformset_factory

from admin_dashboard.mixins import StaffRequiredMixin
from rooms.models.room import Room
from rooms.models.room_category import RoomCategory
from rooms.models.room_facility import RoomFacility
from rooms.models.room_image import RoomImage
from rooms.models.room_policy import RoomPolicy
from rooms.models.room_seasonal_price import RoomSeasonalPrice
from rooms.models.room_availability import RoomAvailability
from rooms.models.room_base_price import RoomBasePrice
from admin_dashboard.forms import RoomForm, RoomCategoryForm, RoomFacilityForm, RoomPriceForm, RoomImageForm, RoomPolicyForm, RoomBasePriceForm

# Formsets for inline editing on Room
RoomImageFormSet = inlineformset_factory(
    Room, RoomImage, form=RoomImageForm,
    fields=('image',), 
    extra=3, can_delete=True
)
RoomPolicyFormSet = inlineformset_factory(
    Room, RoomPolicy, form=RoomPolicyForm,
    fields=('title', 'description'), 
    extra=2, can_delete=True
)
RoomPriceFormSet = inlineformset_factory(
    Room, RoomSeasonalPrice, form=RoomPriceForm,
    fields=('name', 'currency', 'start_date', 'end_date', 'price_override', 'is_active'), 
    extra=2, can_delete=True
)
RoomBasePriceFormSet = inlineformset_factory(
    Room, RoomBasePrice, form=RoomBasePriceForm,
    fields=('currency', 'base_price', 'discount_price'),
    extra=2, can_delete=True
)

class RoomDashboardView(StaffRequiredMixin, View):
    def get(self, request):
        # pyrefly: ignore [missing-attribute]
        rooms = Room.objects.all().select_related('category').prefetch_related('base_prices__currency')
        # pyrefly: ignore [missing-attribute]
        categories = RoomCategory.objects.all()
        # pyrefly: ignore [missing-attribute]
        facilities = RoomFacility.objects.all()
        active_tab = request.GET.get('tab', 'rooms')
        
        return render(request, 'admin_dashboard/rooms/dashboard.html', {
            'rooms': rooms,
            'categories': categories,
            'facilities': facilities,
            'active_tab': active_tab,
        })

def get_category_inventory_map():
    import json
    from rooms.models.room_category import RoomCategory
    return json.dumps({str(c.id): c.total_rooms for c in RoomCategory.objects.all()})

class RoomCreateView(StaffRequiredMixin, View):
    def get(self, request):
        form = RoomForm()
        image_formset = RoomImageFormSet()
        policy_formset = RoomPolicyFormSet()
        price_formset = RoomPriceFormSet()
        currency_price_formset = RoomBasePriceFormSet()
        return render(request, 'admin_dashboard/rooms/form.html', {
            'form': form,
            'image_formset': image_formset,
            'policy_formset': policy_formset,
            'price_formset': price_formset,
            'currency_price_formset': currency_price_formset,
            'category_inventory_map': get_category_inventory_map(),
            'title': 'Add New Room'
        })
        
    def post(self, request):
        form = RoomForm(request.POST, request.FILES)
        if form.is_valid():
            room = form.save()
            image_formset = RoomImageFormSet(request.POST, request.FILES, instance=room)
            policy_formset = RoomPolicyFormSet(request.POST, instance=room)
            price_formset = RoomPriceFormSet(request.POST, instance=room)
            currency_price_formset = RoomBasePriceFormSet(request.POST, instance=room)
            
            if image_formset.is_valid() and policy_formset.is_valid() and price_formset.is_valid() and currency_price_formset.is_valid():
                image_formset.save()
                policy_formset.save()
                price_formset.save()
                currency_price_formset.save()
                messages.success(request, "Room created successfully.")
                return redirect('admin_dashboard:room_dashboard')
            else:
                # Delete room if inline save fails to keep it atomic
                room.delete()
        else:
            image_formset = RoomImageFormSet(request.POST, request.FILES)
            policy_formset = RoomPolicyFormSet(request.POST)
            price_formset = RoomPriceFormSet(request.POST)
            currency_price_formset = RoomBasePriceFormSet(request.POST)
            
        return render(request, 'admin_dashboard/rooms/form.html', {
            'form': form,
            'image_formset': image_formset,
            'policy_formset': policy_formset,
            'price_formset': price_formset,
            'currency_price_formset': currency_price_formset,
            'category_inventory_map': get_category_inventory_map(),
            'title': 'Add New Room'
        })

class RoomUpdateView(StaffRequiredMixin, View):
    def get(self, request, pk):
        room = get_object_or_404(Room, pk=pk)
        form = RoomForm(instance=room)
        image_formset = RoomImageFormSet(instance=room)
        policy_formset = RoomPolicyFormSet(instance=room)
        price_formset = RoomPriceFormSet(instance=room)
        currency_price_formset = RoomBasePriceFormSet(instance=room)
        return render(request, 'admin_dashboard/rooms/form.html', {
            'form': form,
            'image_formset': image_formset,
            'policy_formset': policy_formset,
            'price_formset': price_formset,
            'currency_price_formset': currency_price_formset,
            'category_inventory_map': get_category_inventory_map(),
            'room': room,
            'title': f'Edit Room: {room.title}'
        })
        
    def post(self, request, pk):
        room = get_object_or_404(Room, pk=pk)
        form = RoomForm(request.POST, request.FILES, instance=room)
        image_formset = RoomImageFormSet(request.POST, request.FILES, instance=room)
        policy_formset = RoomPolicyFormSet(request.POST, instance=room)
        price_formset = RoomPriceFormSet(request.POST, instance=room)
        currency_price_formset = RoomBasePriceFormSet(request.POST, instance=room)
        
        if form.is_valid() and image_formset.is_valid() and policy_formset.is_valid() and price_formset.is_valid() and currency_price_formset.is_valid():
            form.save()
            image_formset.save()
            policy_formset.save()
            price_formset.save()
            currency_price_formset.save()
            messages.success(request, "Room updated successfully.")
            return redirect('admin_dashboard:room_dashboard')
            
        return render(request, 'admin_dashboard/rooms/form.html', {
            'form': form,
            'image_formset': image_formset,
            'policy_formset': policy_formset,
            'price_formset': price_formset,
            'currency_price_formset': currency_price_formset,
            'category_inventory_map': get_category_inventory_map(),
            'room': room,
            'title': f'Edit Room: {room.title}'
        })

class RoomDeleteView(StaffRequiredMixin, DeleteView):
    model = Room
    template_name = 'admin_dashboard/confirm_delete.html'
    success_url = reverse_lazy('admin_dashboard:room_dashboard')
    
    def get_success_url(self):
        messages.success(self.request, "Room deleted successfully.")
        return reverse('admin_dashboard:room_dashboard')

# Room Category Views
class RoomCategoryCreateView(StaffRequiredMixin, CreateView):
    model = RoomCategory
    form_class = RoomCategoryForm
    template_name = 'admin_dashboard/generic_form.html'
    
    def get_success_url(self):
        messages.success(self.request, "Room category created successfully.")
        return reverse('admin_dashboard:room_dashboard') + "?tab=categories"

class RoomCategoryUpdateView(StaffRequiredMixin, UpdateView):
    model = RoomCategory
    form_class = RoomCategoryForm
    template_name = 'admin_dashboard/generic_form.html'
    
    def get_success_url(self):
        messages.success(self.request, "Room category updated successfully.")
        return reverse('admin_dashboard:room_dashboard') + "?tab=categories"

class RoomCategoryDeleteView(StaffRequiredMixin, DeleteView):
    model = RoomCategory
    template_name = 'admin_dashboard/confirm_delete.html'
    
    def get_success_url(self):
        messages.success(self.request, "Room category deleted successfully.")
        return reverse('admin_dashboard:room_dashboard') + "?tab=categories"

# Room Facility Views
class RoomFacilityCreateView(StaffRequiredMixin, CreateView):
    model = RoomFacility
    form_class = RoomFacilityForm
    template_name = 'admin_dashboard/generic_form.html'
    
    def get_success_url(self):
        messages.success(self.request, "Facility created successfully.")
        return reverse('admin_dashboard:room_dashboard') + "?tab=facilities"

class RoomFacilityUpdateView(StaffRequiredMixin, UpdateView):
    model = RoomFacility
    form_class = RoomFacilityForm
    template_name = 'admin_dashboard/generic_form.html'
    
    def get_success_url(self):
        messages.success(self.request, "Facility updated successfully.")
        return reverse('admin_dashboard:room_dashboard') + "?tab=facilities"

class RoomFacilityDeleteView(StaffRequiredMixin, DeleteView):
    model = RoomFacility
    template_name = 'admin_dashboard/confirm_delete.html'
    
    def get_success_url(self):
        messages.success(self.request, "Facility deleted successfully.")
        return reverse('admin_dashboard:room_dashboard') + "?tab=facilities"

# Room Price (Seasonal Prices) Views
class RoomSeasonalPriceCreateView(StaffRequiredMixin, CreateView):
    model = RoomSeasonalPrice
    form_class = RoomPriceForm
    template_name = 'admin_dashboard/generic_form.html'
    
    def get_success_url(self):
        messages.success(self.request, "Seasonal price created successfully.")
        return reverse('admin_dashboard:room_dashboard')

class RoomSeasonalPriceUpdateView(StaffRequiredMixin, UpdateView):
    model = RoomSeasonalPrice
    form_class = RoomPriceForm
    template_name = 'admin_dashboard/generic_form.html'
    
    def get_success_url(self):
        messages.success(self.request, "Seasonal price updated successfully.")
        return reverse('admin_dashboard:room_dashboard')

class RoomSeasonalPriceDeleteView(StaffRequiredMixin, DeleteView):
    model = RoomSeasonalPrice
    template_name = 'admin_dashboard/confirm_delete.html'
    
    def get_success_url(self):
        messages.success(self.request, "Seasonal price deleted successfully.")
        return reverse('admin_dashboard:room_dashboard')

# Calendar and Availability View
class RoomAvailabilityCalendarView(StaffRequiredMixin, View):
    def get(self, request):
        today = timezone.localdate() if hasattr(timezone, 'localdate') else datetime.date.today()
        year = int(request.GET.get('year', today.year))
        month = int(request.GET.get('month', today.month))
        
        # Calendar days calculation
        first_day_of_month = datetime.date(year, month, 1)
        next_month = month + 1 if month < 12 else 1
        next_month_year = year if month < 12 else year + 1
        last_day_of_month = datetime.date(next_month_year, next_month, 1) - datetime.timedelta(days=1)
        
        days_in_month = []
        curr_day = first_day_of_month
        while curr_day <= last_day_of_month:
            days_in_month.append(curr_day)
            curr_day += datetime.timedelta(days=1)
            
        # pyrefly: ignore [missing-attribute]
        rooms = Room.objects.all().select_related('category')
        
        # Build grid data: room_id -> { date -> { booked_count, is_available } }
        grid = {}
        for r in rooms:
            grid[r.id] = {}
            for d in days_in_month:
                # Find if there is a room availability record
                # pyrefly: ignore [missing-attribute]
                avail = RoomAvailability.objects.filter(room=r, date=d).first()
                if avail:
                    grid[r.id][d] = {
                        'rooms_booked': avail.rooms_booked,
                        'is_available': avail.is_available,
                        'booking_uid': avail.booking.booking_uid if avail.booking else None
                    }
                else:
                    grid[r.id][d] = {
                        'rooms_booked': 0,
                        'is_available': True,
                        'booking_uid': None
                    }
                    
        # Context dates
        prev_month = month - 1 if month > 1 else 12
        prev_year = year if month > 1 else year - 1
        
        month_name = first_day_of_month.strftime('%B')
        
        return render(request, 'admin_dashboard/rooms/calendar.html', {
            'rooms': rooms,
            'days_in_month': days_in_month,
            'grid': grid,
            'current_year': year,
            'current_month': month,
            'month_name': month_name,
            'prev_month': prev_month,
            'prev_year': prev_year,
            'next_month': next_month,
            'next_year': next_month_year,
        })

# Bulk actions
class RoomBulkPriceUpdateView(StaffRequiredMixin, View):
    def post(self, request):
        room_ids = request.POST.getlist('selected_rooms')
        adjustment_type = request.POST.get('adjustment_type', 'percentage') # percentage or fixed
        try:
            adjustment_value = Decimal(request.POST.get('adjustment_value', '0') or '0')
        except Exception:
            adjustment_value = Decimal('0')
        
        if not room_ids:
            messages.warning(request, "No rooms selected for bulk pricing update.")
            return redirect('admin_dashboard:room_dashboard')
            
        from rooms.models.room_base_price import RoomBasePrice
        room_base_prices = RoomBasePrice.objects.filter(room_id__in=room_ids)
        for cp in room_base_prices:
            if adjustment_type == 'percentage':
                cp.base_price = cp.base_price * (Decimal('1') + adjustment_value / Decimal('100'))
            else:
                cp.base_price = cp.base_price + adjustment_value
            cp.save()
            
        messages.success(request, f"Bulk updated base price for {len(room_ids)} room(s).")
        return redirect('admin_dashboard:room_dashboard')

class RoomBulkPublishView(StaffRequiredMixin, View):
    def post(self, request):
        room_ids = request.POST.getlist('selected_rooms')
        action = request.POST.get('bulk_action') # publish or unpublish
        
        if not room_ids:
            messages.warning(request, "No rooms selected for bulk status toggle.")
            return redirect('admin_dashboard:room_dashboard')
            
        is_pub = (action == 'publish')
        # pyrefly: ignore [missing-attribute]
        updated = Room.objects.filter(id__in=room_ids).update(is_published=is_pub)
        
        messages.success(request, f"Bulk set visibility status to {'Published' if is_pub else 'Unpublished'} for {updated} room(s).")
        return redirect('admin_dashboard:room_dashboard')
