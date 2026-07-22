import datetime
from django.views.generic import TemplateView
from django.db.models import Sum
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.urls import reverse

from admin_dashboard.mixins import StaffRequiredMixin
from booking.models.booking import Booking
from rooms.models.room_category import RoomCategory
from payments.models.payment import Payment
from dining.models.reservation import DiningReservation
from contact.models.inquiry import ContactInquiry

User = get_user_model()

class DashboardHomeView(StaffRequiredMixin, TemplateView):
    template_name = 'admin_dashboard/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()
        start_of_month = today.replace(day=1)
        
        # 1. Today's Check-ins / Check-outs
        # pyrefly: ignore [missing-attribute]
        today_checkins = Booking.objects.filter(check_in=today)
        # pyrefly: ignore [missing-attribute]
        today_checkouts = Booking.objects.filter(check_out=today)
        
        # 2. Room Occupancy
        # pyrefly: ignore [missing-attribute]
        total_rooms_capacity = RoomCategory.objects.aggregate(total=Sum('total_rooms'))['total'] or 0
        
        # Rooms occupied today: checkings status is checked_in or confirmed (if they check in today)
        # pyrefly: ignore [missing-attribute]
        occupied_bookings = Booking.objects.filter(
            status__in=['checked_in', 'confirmed'],
            check_in__lte=today,
            check_out__gt=today
        )
        occupied_rooms_count = occupied_bookings.aggregate(total=Sum('num_rooms'))['total'] or 0
        available_rooms_count = max(0, total_rooms_capacity - occupied_rooms_count)
        
        # 3. Booking Stats
        # pyrefly: ignore [missing-attribute]
        pending_bookings_count = Booking.objects.filter(status__in=['draft', 'pending']).count()
        # pyrefly: ignore [missing-attribute]
        confirmed_bookings_count = Booking.objects.filter(status='confirmed').count()
        
        # 4. Revenue Today & Month
        # Sum payments that succeeded
        # pyrefly: ignore [missing-attribute]
        revenue_today = Payment.objects.filter(
            status='success', 
            created_at__date=today
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # pyrefly: ignore [missing-attribute]
        payments_today = Payment.objects.filter(
            status='success', 
            created_at__date=today
        ).select_related('currency', 'booking')
        
        revenue_today_by_currency = {}
        for p in payments_today:
            c_code = p.currency.iso_code if p.currency else (p.booking.currency_code if p.booking else 'USD')
            revenue_today_by_currency[c_code] = revenue_today_by_currency.get(c_code, 0) + p.amount
        
        # pyrefly: ignore [missing-attribute]
        revenue_month = Payment.objects.filter(
            status='success',
            created_at__date__gte=start_of_month,
            created_at__date__lte=today
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # pyrefly: ignore [missing-attribute]
        payments_month = Payment.objects.filter(
            status='success',
            created_at__date__gte=start_of_month,
            created_at__date__lte=today
        ).select_related('currency', 'booking')
        
        revenue_month_by_currency = {}
        for p in payments_month:
            c_code = p.currency.iso_code if p.currency else (p.booking.currency_code if p.booking else 'USD')
            revenue_month_by_currency[c_code] = revenue_month_by_currency.get(c_code, 0) + p.amount
        
        # 5. Pending Payments (bookings pending/confirmed but payment not successful)
        # pyrefly: ignore [missing-attribute]
        pending_payments_count = Booking.objects.filter(status='pending').count()
        
        # 6. Service / Dining Reservations
        # pyrefly: ignore [missing-attribute]
        dining_reservations_today = DiningReservation.objects.filter(date=today)
        
        # 7. Contact inquiries
        # pyrefly: ignore [missing-attribute]
        contact_messages_today = ContactInquiry.objects.filter(created_at__date=today)
        
        # 9. Coupon Usage
        # pyrefly: ignore [missing-attribute]
        coupon_usage_count = Booking.objects.filter(coupon__isnull=False).count()
        
        # 10. Dynamic Chart Data
        # We fetch the actual daily bookings and successful payments count for the last 7 days
        # and pre-calculate display heights to scale beautifully on screen.
        chart_data = []
        raw_revs = []
        raw_books = []
        for i in range(6, -1, -1):
            date_point = today - datetime.timedelta(days=i)
            # pyrefly: ignore [missing-attribute]
            b_cnt = Booking.objects.filter(created_at__date=date_point).count()
            # pyrefly: ignore [missing-attribute]
            p_sum = Payment.objects.filter(status='success', created_at__date=date_point).aggregate(total=Sum('amount'))['total'] or 0
            raw_books.append(b_cnt)
            raw_revs.append(float(p_sum))
            
        max_rev = max(raw_revs) if raw_revs and max(raw_revs) > 0 else 1000.0
        max_book = max(raw_books) if raw_books and max(raw_books) > 0 else 5.0
        
        for i in range(6, -1, -1):
            date_point = today - datetime.timedelta(days=i)
            # pyrefly: ignore [missing-attribute]
            b_cnt = Booking.objects.filter(created_at__date=date_point).count()
            # pyrefly: ignore [missing-attribute]
            day_payments = Payment.objects.filter(status='success', created_at__date=date_point).select_related('currency', 'booking')
            day_rev_by_curr = {}
            p_sum = 0
            for p in day_payments:
                c_code = p.currency.iso_code if p.currency else (p.booking.currency_code if p.booking else 'USD')
                day_rev_by_curr[c_code] = day_rev_by_curr.get(c_code, 0) + p.amount
                p_sum += p.amount
            
            rev_height = int((float(p_sum) / max_rev) * 80)
            book_height = int((float(b_cnt) / float(max_book)) * 80)
            
            if p_sum > 0 and rev_height < 10:
                rev_height = 10
            if b_cnt > 0 and book_height < 10:
                book_height = 10
                
            chart_data.append({
                'label': date_point.strftime('%b %d'),
                'revenue': p_sum,
                'revenue_by_currency': day_rev_by_curr,
                'bookings': b_cnt,
                'rev_height': rev_height,
                'book_height': book_height,
            })
            
        # 11. Recent Activities List
        # pyrefly: ignore [missing-attribute]
        recent_bookings = Booking.objects.all()[:5]
        # pyrefly: ignore [missing-attribute]
        recent_payments = Payment.objects.all().select_related('booking')[:5]
        # pyrefly: ignore [missing-attribute]
        recent_contacts = ContactInquiry.objects.all()[:5]
        
        activities = []
        for b in recent_bookings:
            activities.append({
                'type': 'booking',
                'title': f"New booking by {b.guest_name}",
                'desc': f"{b.room.title} · {b.num_rooms} room(s)",
                'time': b.created_at,
                'url': reverse('admin_dashboard:booking_detail', args=[b.id])
            })
        for p in recent_payments:
            activities.append({
                'type': 'payment',
                'title': f"Payment of {p.currency.symbol if p.currency else '$'}{p.amount} received",
                'desc': f"Txn: {p.transaction_id} · Gateway: {p.gateway}",
                'time': p.created_at,
                'url': reverse('admin_dashboard:payment_detail', args=[p.id])
            })
        for c in recent_contacts:
            activities.append({
                'type': 'inquiry',
                'title': f"Message from {c.name}",
                'desc': f"Subj: {c.subject}",
                'time': c.created_at,
                'url': reverse('admin_dashboard:contact_dashboard') + "?tab=inquiries"
            })
            
        # Sort activities by time desc
        activities = sorted(activities, key=lambda x: x['time'], reverse=True)[:8]

        # Put everything into context
        context.update({
            'today_checkins_count': today_checkins.count(),
            'today_checkouts_count': today_checkouts.count(),
            'today_checkins': today_checkins[:5],
            'today_checkouts': today_checkouts[:5],
            
            'occupied_rooms_count': occupied_rooms_count,
            'available_rooms_count': available_rooms_count,
            'occupancy_rate': int((occupied_rooms_count / total_rooms_capacity * 100)) if total_rooms_capacity > 0 else 0,
            
            'pending_bookings_count': pending_bookings_count,
            'confirmed_bookings_count': confirmed_bookings_count,
            
            'revenue_today': revenue_today,
            'revenue_today_by_currency': revenue_today_by_currency,
            'revenue_month': revenue_month,
            'revenue_month_by_currency': revenue_month_by_currency,
            'pending_payments_count': pending_payments_count,
            
            'dining_reservations_today_count': dining_reservations_today.count(),
            'dining_reservations_today': dining_reservations_today[:5],
            
            'contact_messages_today_count': contact_messages_today.count(),
            'coupon_usage_count': coupon_usage_count,
            
            # Chart Data
            'chart_data': chart_data,
            
            # Activities
            'activities': activities,
        })
        return context
