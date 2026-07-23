from django.views.generic import TemplateView
from homepage.models.hero_slide import HeroSlide
from homepage.models.about_preview import AboutPreview
from rooms.models.room import Room
from rooms.models.room_facility import RoomFacility
from dining.models.item import DiningItem
from testimonials.models.testimonial import Testimonial


class HomeView(TemplateView):
    template_name = 'homepage/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
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

        context['hero_slides'] = HeroSlide.objects.filter(is_active=True).order_by('order')
        context['about_preview'] = AboutPreview.objects.first()
        
        from django.db.models import Prefetch
        from rooms.models.room_base_price import RoomBasePrice
        
        rooms = list(Room.objects.filter(
            is_featured=True,
            is_published=True,
            base_prices__currency__iso_code=selected_currency
        ).prefetch_related(
            Prefetch(
                'base_prices',
                queryset=RoomBasePrice.objects.filter(currency__iso_code=selected_currency),
                to_attr='active_currency_price'
            ),
            'images',
            'facilities',
            'seasonal_prices__currency',
        )[:3])
        
        for room in rooms:
            room.set_active_currency(selected_currency)
            
        context['featured_rooms'] = rooms
        context['featured_dining'] = DiningItem.objects.filter(is_chef_special=True, is_published=True)[:3]
        context['facilities'] = RoomFacility.objects.filter(is_featured=True)
        context['testimonials'] = Testimonial.objects.filter(is_featured=True, is_published=True)[:5]
        return context


from homepage.models import HeroSlide, AboutPreview, AboutCMS, ZiplineCMS, SustainabilityCMS, SustainabilityPillar

# (keep HomeView...)

class AboutView(TemplateView):
    template_name = 'homepage/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        about_cms = AboutCMS.objects.first()
        if not about_cms:
            about_cms = AboutCMS.objects.create()
        context['about_cms'] = about_cms
        context['about_preview'] = AboutPreview.objects.first()
        context['testimonials'] = Testimonial.objects.filter(is_featured=True, is_published=True)[:4]
        context['team_members'] = [
            {
                'name': 'Prem Durbar Management',
                'role': 'Executive Hospitality Leadership',
                'bio': 'Dedicated to preserving Newari heritage craftsmanship, sustainable tourism, and delivering high-altitude Himalayan hospitality in Nagarkot.',
                'image': 'https://images.unsplash.com/photo-1560250097-0b93528c311a?q=80&w=800&auto=format&fit=crop'
            },
            {
                'name': 'Adventure Zipline Crew',
                'role': 'Certified Flight & Safety Instructors',
                'bio': 'Internationally trained zip line flight operators ensuring 100% safety standards on Nepal’s longest Superman Zip Line.',
                'image': 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?q=80&w=800&auto=format&fit=crop'
            },
            {
                'name': 'Culinary & Dining Team',
                'role': 'Farm-to-Table Master Chefs',
                'bio': 'Crafting authentic Nepali Khaja sets, Mutton & Chicken Thalis, Kodo Salsa, and continental gourmets with organic local produce.',
                'image': 'https://images.unsplash.com/photo-1583394838336-acd977736f90?q=80&w=800&auto=format&fit=crop'
            }
        ]
        return context


class ZiplineView(TemplateView):
    template_name = 'homepage/zipline.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        zipline_cms = ZiplineCMS.objects.first()
        if not zipline_cms:
            zipline_cms = ZiplineCMS.objects.create()
        context['zipline_cms'] = zipline_cms
        return context


class SustainabilityView(TemplateView):
    template_name = 'homepage/sustainability.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sustainability_cms = SustainabilityCMS.objects.first()
        if not sustainability_cms:
            sustainability_cms = SustainabilityCMS.objects.create()
        context['sustainability_cms'] = sustainability_cms
        context['pillars'] = SustainabilityPillar.objects.filter(is_published=True)
        return context
