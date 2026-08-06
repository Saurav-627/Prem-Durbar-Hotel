from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import DeleteView, View

from admin_dashboard.forms import DiningItemBasePriceFormSet, DiningItemForm
from admin_dashboard.mixins import StaffRequiredMixin
from dining.models.item import DiningCategory, DiningItem


class DiningDashboardView(StaffRequiredMixin, View):
    permission_required = 'dining.view_diningitem'
    def get(self, request):
        categories = DiningCategory.objects.all()
        menu_items_qs = DiningItem.objects.all().select_related('category').prefetch_related('base_prices__currency')
        
        paginator = Paginator(menu_items_qs, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        return render(request, 'admin_dashboard/dining/dashboard.html', {
            'categories': categories,
            'menu_items': page_obj.object_list,
            'page_obj': page_obj,
            'is_paginated': page_obj.has_other_pages(),
        })


class DiningItemCreateView(StaffRequiredMixin, View):
    permission_required = 'dining.add_diningitem'

    def get(self, request):
        form = DiningItemForm()
        currency_price_formset = DiningItemBasePriceFormSet()
        return render(request, 'admin_dashboard/dining/item_form.html', {
            'form': form,
            'currency_price_formset': currency_price_formset,
            'title': 'Add New Food Menu Item'
        })
        
    def post(self, request):
        form = DiningItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            currency_price_formset = DiningItemBasePriceFormSet(request.POST, instance=item)
            
            if currency_price_formset.is_valid():
                item.save()
                _prices = currency_price_formset.save()
                
                # Update item.base_price with NPR price or first price entered
                npr_price = item.base_prices.filter(currency__iso_code='NPR').first()
                if npr_price:
                    item.base_price = npr_price.base_price
                elif item.base_prices.exists():
                    bp = item.base_prices.first()
                    if bp is not None and getattr(bp, "base_price", None):
                        item.base_price = bp.base_price
                item.save()
                
                messages.success(request, "Food menu item created successfully.")
                return redirect(reverse('admin_dashboard:dining_dashboard'))
        else:
            currency_price_formset = DiningItemBasePriceFormSet(request.POST)
            
        return render(request, 'admin_dashboard/dining/item_form.html', {
            'form': form,
            'currency_price_formset': currency_price_formset,
            'title': 'Add New Food Menu Item'
        })


class DiningItemUpdateView(StaffRequiredMixin, View):
    permission_required = 'dining.change_diningitem'
    def get(self, request, pk):
        item = get_object_or_404(DiningItem, pk=pk)
        form = DiningItemForm(instance=item)
        currency_price_formset = DiningItemBasePriceFormSet(instance=item)
        return render(request, 'admin_dashboard/dining/item_form.html', {
            'form': form,
            'currency_price_formset': currency_price_formset,
            'item': item,
            'title': f'Edit Menu Item: {item.title}'
        })
        
    def post(self, request, pk):
        item = get_object_or_404(DiningItem, pk=pk)
        form = DiningItemForm(request.POST, request.FILES, instance=item)
        currency_price_formset = DiningItemBasePriceFormSet(request.POST, instance=item)
        
        if form.is_valid() and currency_price_formset.is_valid():
            form.save()
            currency_price_formset.save()
            
            # Update item.base_price with NPR price or first price entered
            npr_price = item.base_prices.filter(currency__iso_code='NPR').first()
            if npr_price:
                item.base_price = npr_price.base_price
            elif item.base_prices.exists():
                bp = item.base_prices.first()
                if bp is not None and getattr(bp, "base_price", None):
                    item.base_price = bp.base_price
            item.save()
            
            messages.success(request, "Food menu item updated successfully.")
            return redirect(reverse('admin_dashboard:dining_dashboard'))
            
        return render(request, 'admin_dashboard/dining/item_form.html', {
            'form': form,
            'currency_price_formset': currency_price_formset,
            'item': item,
            'title': f'Edit Menu Item: {item.title}'
        })


class DiningItemDeleteView(StaffRequiredMixin, DeleteView):
    model = DiningItem
    template_name = 'admin_dashboard/confirm_delete.html'
    permission_required = 'dining.delete_diningitem'
    
    # pyrefly: ignore [bad-override]
    def get_success_url(self):
        messages.success(self.request, "Food menu item deleted successfully.")
        return reverse_lazy('admin_dashboard:dining_dashboard')

