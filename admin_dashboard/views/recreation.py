from django.shortcuts import render
from django.views.generic import View, CreateView, UpdateView, DeleteView
from django.urls import reverse
from django.contrib import messages

from admin_dashboard.mixins import StaffRequiredMixin
from recreation.models.activity import RecreationActivity
from admin_dashboard.forms import RecreationActivityForm

class RecreationDashboardView(StaffRequiredMixin, View):
    def get(self, request):
        # pyrefly: ignore [missing-attribute]
        activities = RecreationActivity.objects.all()
        return render(request, 'admin_dashboard/recreation/dashboard.html', {
            'activities': activities
        })

class RecreationCreateView(StaffRequiredMixin, CreateView):
    model = RecreationActivity
    form_class = RecreationActivityForm
    template_name = 'admin_dashboard/generic_form.html'
    
    def get_success_url(self):
        messages.success(self.request, "Recreational activity created successfully.")
        return reverse('admin_dashboard:recreation_dashboard')

class RecreationUpdateView(StaffRequiredMixin, UpdateView):
    model = RecreationActivity
    form_class = RecreationActivityForm
    template_name = 'admin_dashboard/generic_form.html'
    
    def get_success_url(self):
        messages.success(self.request, "Recreational activity updated successfully.")
        return reverse('admin_dashboard:recreation_dashboard')

class RecreationDeleteView(StaffRequiredMixin, DeleteView):
    model = RecreationActivity
    template_name = 'admin_dashboard/confirm_delete.html'
    
    def get_success_url(self):
        messages.success(self.request, "Recreational activity deleted successfully.")
        return reverse('admin_dashboard:recreation_dashboard')
