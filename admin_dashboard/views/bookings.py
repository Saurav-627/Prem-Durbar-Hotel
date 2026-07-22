from django.shortcuts import redirect, get_object_or_404
from django.views.generic import View, ListView, DetailView
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q

from admin_dashboard.mixins import StaffRequiredMixin
from booking.models.booking import Booking
from payments.models.payment import Payment

class BookingListView(StaffRequiredMixin, ListView):
    model = Booking
    template_name = 'admin_dashboard/bookings/list.html'
    context_object_name = 'bookings'
    paginate_by = 15

    def get_queryset(self):
        queryset = Booking.objects.all().select_related('room', 'room__category').prefetch_related('room__base_prices__currency')
        
        # Search query
        q = self.request.GET.get('search', '').strip()
        if q:
            queryset = queryset.filter(
                # pyrefly: ignore [unsupported-operation]
                Q(booking_uid__icontains=q) |
                Q(guest_name__icontains=q) |
                Q(guest_email__icontains=q) |
                Q(guest_phone__icontains=q)
            )
            
        # Filter by status
        status = self.request.GET.get('status', '').strip()
        if status:
            queryset = queryset.filter(status=status)
            
        # Filter by check-in date
        check_in_date = self.request.GET.get('check_in', '').strip()
        if check_in_date:
            queryset = queryset.filter(check_in=check_in_date)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Booking.STATUS_CHOICES
        context['selected_status'] = self.request.GET.get('status', '')
        context['selected_check_in'] = self.request.GET.get('check_in', '')
        context['search_query'] = self.request.GET.get('search', '')
        return context

class BookingDetailView(StaffRequiredMixin, DetailView):
    model = Booking
    template_name = 'admin_dashboard/bookings/detail.html'
    context_object_name = 'booking'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Prefetch currency prices for the booking room
        from django.db.models import Prefetch
        from rooms.models.room_base_price import RoomBasePrice
        # Resolve the booking's currency by looking at the subtotal-stored currency (fallback: first available price)
        booking = self.object
        if booking and booking.room:
            # Use the first available price as the display currency for the invoice (price was copied at booking time)
            first_cp = booking.room.base_prices.first()
            if first_cp:
                booking.room.set_active_currency(first_cp.currency.iso_code)
        # Fetch payments associated with this booking
        # pyrefly: ignore [missing-attribute]
        context['payments'] = Payment.objects.filter(booking=self.object).order_by('-created_at')
        return context

class BookingUpdateStatusView(StaffRequiredMixin, View):
    def post(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk)
        action = request.POST.get('action') # check_in, check_out, cancel, confirm
        
        valid_actions = {
            'confirm': 'confirmed',
            'check_in': 'checked_in',
            'check_out': 'checked_out',
            'cancel': 'cancelled'
        }
        
        if action in valid_actions:
            new_status = valid_actions[action]
            # Verify validity of state transition
            # standard state machine: draft -> pending -> confirmed -> checked_in -> checked_out
            # cancellation is allowed if not checked_out
            if action == 'cancel' and booking.status == 'checked_out':
                messages.error(request, "Cannot cancel a booking that is already checked out.")
            elif action == 'check_in' and booking.status not in ['confirmed', 'pending', 'draft']:
                messages.error(request, f"Cannot check in from status: {booking.get_status_display()}")
            elif action == 'check_out' and booking.status != 'checked_in':
                messages.error(request, "Cannot check out. Guest must be checked in first.")
            else:
                old_status = booking.status
                booking.status = new_status
                booking.save() # This triggers availability updates automatically in Booking model override
                messages.success(request, f"Booking status updated from {old_status} to {new_status.replace('_', ' ').capitalize()}.")
        else:
            messages.error(request, "Invalid action requested.")
            
        return redirect('admin_dashboard:booking_detail', pk=pk)

class BookingInvoiceView(StaffRequiredMixin, DetailView):
    model = Booking
    template_name = 'admin_dashboard/bookings/invoice.html'
    context_object_name = 'booking'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Set currency matching the booking's currency_code
        self.object.room.set_active_currency(self.object.currency_code)
        # pyrefly: ignore [missing-attribute]
        context['payments'] = Payment.objects.filter(booking=self.object, status='success')
        context['print_date'] = timezone.now()
        return context
