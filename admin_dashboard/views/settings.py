from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, UpdateView, View

from admin_dashboard.forms import (
    CurrencyForm,
    HotelSettingsForm,
    NavigationMenuForm,
    PaymentProcessorForm,
)
from admin_dashboard.mixins import StaffRequiredMixin
from payments.models.payment_processor import PaymentProcessor
from settings_manager.models.currency import Currency
from settings_manager.models.hotel_settings import HotelSettings
from settings_manager.models.navigation import NavigationMenu


class SettingsDashboardView(StaffRequiredMixin, View):
    permission_required = 'settings_manager.view_hotelsettings'

    def get(self, request):
        # pyrefly: ignore [missing-attribute]
        settings_obj = HotelSettings.objects.first()
        if not settings_obj:
            # pyrefly: ignore [missing-attribute]
            settings_obj = HotelSettings.objects.create()
            
        settings_form = HotelSettingsForm(instance=settings_obj)
        currencies = Currency.objects.all()
        # pyrefly: ignore [missing-attribute]
        menus = NavigationMenu.objects.all().select_related('parent')
        processors = PaymentProcessor.objects.all().prefetch_related('payment_currencies')
        
        # Determine active tab
        active_tab = request.GET.get('tab', 'general')
        
        return render(request, 'admin_dashboard/settings_manager.html', {
            'settings_form': settings_form,
            'currencies': currencies,
            'menus': menus,
            'processors': processors,
            'active_tab': active_tab,
        })
        
    def post(self, request):
        if not (request.user.is_superuser or request.user.has_perm('settings_manager.change_hotelsettings')):
            raise PermissionDenied("You do not have permission to update hotel settings.")

        # pyrefly: ignore [missing-attribute]
        settings_obj = HotelSettings.objects.first()
        if not settings_obj:
            # pyrefly: ignore [missing-attribute]
            settings_obj = HotelSettings.objects.create()
            
        settings_form = HotelSettingsForm(request.POST, request.FILES, instance=settings_obj)
        if settings_form.is_valid():
            settings_form.save()
            messages.success(request, "Global settings updated successfully.")
            return redirect('admin_dashboard:settings_dashboard')
        
        # If invalid
        currencies = Currency.objects.all()
        # pyrefly: ignore [missing-attribute]
        menus = NavigationMenu.objects.all()
        processors = PaymentProcessor.objects.all().prefetch_related('payment_currencies')
        return render(request, 'admin_dashboard/settings_manager.html', {
            'settings_form': settings_form,
            'currencies': currencies,
            'menus': menus,
            'processors': processors,
            'active_tab': 'general',
        })

# Currencies Views
class CurrencyCreateView(StaffRequiredMixin, CreateView):
    permission_required = 'settings_manager.add_currency'
    model = Currency
    form_class = CurrencyForm
    template_name = 'admin_dashboard/generic_form.html'
    
    def get_success_url(self):
        messages.success(self.request, "Currency created successfully.")
        return reverse('admin_dashboard:settings_dashboard') + "?tab=currencies"

class CurrencyUpdateView(StaffRequiredMixin, UpdateView):
    permission_required = 'settings_manager.change_currency'
    model = Currency
    form_class = CurrencyForm
    template_name = 'admin_dashboard/generic_form.html'
    
    def get_success_url(self):
        messages.success(self.request, "Currency updated successfully.")
        return reverse('admin_dashboard:settings_dashboard') + "?tab=currencies"

class CurrencyDeleteView(StaffRequiredMixin, DeleteView):
    permission_required = 'settings_manager.delete_currency'
    model = Currency
    template_name = 'admin_dashboard/confirm_delete.html'
    
    def get_success_url(self):
        messages.success(self.request, "Currency deleted successfully.")
        return reverse('admin_dashboard:settings_dashboard') + "?tab=currencies"

# Navigation Menu Views
class NavigationMenuCreateView(StaffRequiredMixin, CreateView):
    permission_required = 'settings_manager.add_navigationmenu'
    model = NavigationMenu
    form_class = NavigationMenuForm
    template_name = 'admin_dashboard/generic_form.html'
    
    def get_success_url(self):
        messages.success(self.request, "Navigation menu item created successfully.")
        return reverse('admin_dashboard:settings_dashboard') + "?tab=navigation"

class NavigationMenuUpdateView(StaffRequiredMixin, UpdateView):
    permission_required = 'settings_manager.change_navigationmenu'
    model = NavigationMenu
    form_class = NavigationMenuForm
    template_name = 'admin_dashboard/generic_form.html'
    
    def get_success_url(self):
        messages.success(self.request, "Navigation menu item updated successfully.")
        return reverse('admin_dashboard:settings_dashboard') + "?tab=navigation"

class NavigationMenuDeleteView(StaffRequiredMixin, DeleteView):
    permission_required = 'settings_manager.delete_navigationmenu'
    model = NavigationMenu
    template_name = 'admin_dashboard/confirm_delete.html'
    
    def get_success_url(self):
        messages.success(self.request, "Navigation menu item deleted successfully.")
        return reverse('admin_dashboard:settings_dashboard') + "?tab=navigation"


# Payment Processor Views
class PaymentProcessorCreateView(StaffRequiredMixin, CreateView):
    permission_required = 'payments.add_paymentprocessor'
    model = PaymentProcessor
    form_class = PaymentProcessorForm
    template_name = 'admin_dashboard/generic_form.html'
    
    def get_success_url(self):
        messages.success(self.request, "Payment processor created successfully.")
        return reverse('admin_dashboard:settings_dashboard') + "?tab=processors"

class PaymentProcessorUpdateView(StaffRequiredMixin, UpdateView):
    permission_required = 'payments.change_paymentprocessor'
    model = PaymentProcessor
    form_class = PaymentProcessorForm
    template_name = 'admin_dashboard/generic_form.html'
    
    def get_success_url(self):
        messages.success(self.request, "Payment processor updated successfully.")
        return reverse('admin_dashboard:settings_dashboard') + "?tab=processors"

class PaymentProcessorDeleteView(StaffRequiredMixin, DeleteView):
    permission_required = 'payments.delete_paymentprocessor'
    model = PaymentProcessor
    template_name = 'admin_dashboard/confirm_delete.html'
    
    def get_success_url(self):
        messages.success(self.request, "Payment processor deleted successfully.")
        return reverse('admin_dashboard:settings_dashboard') + "?tab=processors"

