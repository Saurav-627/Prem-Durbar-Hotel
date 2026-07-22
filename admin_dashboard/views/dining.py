from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages

from admin_dashboard.mixins import StaffRequiredMixin
from dining.models.venue import DiningVenue
from dining.models.reservation import DiningReservation
from admin_dashboard.forms import DiningVenueForm

class DiningDashboardView(StaffRequiredMixin, View):
    def get(self, request):
        # pyrefly: ignore [missing-attribute]
        venues = DiningVenue.objects.all()
        # pyrefly: ignore [missing-attribute]
        reservations = DiningReservation.objects.all().select_related('venue')
        active_tab = request.GET.get('tab', 'venues')
        
        return render(request, 'admin_dashboard/dining/dashboard.html', {
            'venues': venues,
            'reservations': reservations,
            'active_tab': active_tab,
        })

class DiningVenueCreateView(StaffRequiredMixin, CreateView):
    model = DiningVenue
    form_class = DiningVenueForm
    template_name = 'admin_dashboard/generic_form.html'
    success_url = reverse_lazy('admin_dashboard:dining_dashboard')
    
    def get_success_url(self):
        messages.success(self.request, "Dining venue created successfully.")
        return reverse_lazy('admin_dashboard:dining_dashboard') + "?tab=venues"

class DiningVenueUpdateView(StaffRequiredMixin, UpdateView):
    model = DiningVenue
    form_class = DiningVenueForm
    template_name = 'admin_dashboard/generic_form.html'
    
    def get_success_url(self):
        messages.success(self.request, "Dining venue updated successfully.")
        return reverse_lazy('admin_dashboard:dining_dashboard') + "?tab=venues"

class DiningVenueDeleteView(StaffRequiredMixin, DeleteView):
    model = DiningVenue
    template_name = 'admin_dashboard/confirm_delete.html'
    
    def get_success_url(self):
        messages.success(self.request, "Dining venue deleted successfully.")
        return reverse_lazy('admin_dashboard:dining_dashboard') + "?tab=venues"

class DiningReservationUpdateStatusView(StaffRequiredMixin, View):
    def post(self, request, pk):
        reservation = get_object_or_404(DiningReservation, pk=pk)
        status = request.POST.get('status')
        if status in ['confirmed', 'cancelled', 'pending']:
            reservation.status = status
            reservation.save()
            messages.success(request, f"Dining reservation updated to {status.capitalize()}.")
        else:
            messages.error(request, "Invalid status choice.")
        return redirect(reverse_lazy('admin_dashboard:dining_dashboard') + "?tab=reservations")
