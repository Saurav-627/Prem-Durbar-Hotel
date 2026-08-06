from django.views.generic import DetailView, ListView

from settings_manager.models.currency import Currency

from ..models.item import DiningCategory, DiningItem


class DiningListView(ListView):
    model = DiningCategory
    template_name = 'dining/dining_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return DiningCategory.objects.filter(is_published=True).prefetch_related(
            'items'
        ).order_by('order', 'name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get active currency from cookie
        selected_currency = self.request.COOKIES.get('currency', 'USD')
        valid_currencies = list(Currency.objects.filter(is_published=True).values_list('iso_code', flat=True))
        if selected_currency not in valid_currencies:
            selected_currency = 'USD'
            
        currency_obj = Currency.objects.filter(iso_code=selected_currency).first()
        context['selected_currency'] = selected_currency
        context['selected_currency_symbol'] = currency_obj.symbol if currency_obj else '$'
        
        # All Published Menu Items
        all_items = list(
            DiningItem.objects.filter(is_published=True)
            .select_related('category', 'currency')
            .prefetch_related('base_prices__currency')
        )
        for item in all_items:
            item.set_active_currency(selected_currency)
            
        context['all_items'] = all_items
        context['featured_items'] = [it for it in all_items if it.is_chef_special]
        
        # Bind active currency to category items
        categories = list(context['categories'])
        for cat in categories:
            cat_items = [it for it in all_items if it.category_id == cat.id]
            cat.active_items = cat_items
            
        context['categories'] = categories
        return context


class DiningDetailView(DetailView):
    model = DiningItem
    template_name = 'dining/dining_detail.html'
    context_object_name = 'item'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return DiningItem.objects.filter(is_published=True)
