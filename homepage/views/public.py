from django.views.generic import TemplateView
from homepage.models.hero_slide import HeroSlide
from homepage.models.about_preview import AboutPreview
from rooms.models.room import Room
from rooms.models.room_facility import RoomFacility
from dining.models.venue import DiningVenue
from testimonials.models.testimonial import Testimonial
from nearby_places.models.attraction import Attraction


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
        context['featured_dining'] = DiningVenue.objects.filter(is_featured=True, is_published=True)[:3]
        context['facilities'] = RoomFacility.objects.filter(is_featured=True)
        context['testimonials'] = Testimonial.objects.filter(is_featured=True, is_published=True)[:5]
        context['attractions'] = Attraction.objects.filter(is_active=True).order_by('order')[:6]
        return context


class AboutView(TemplateView):
    template_name = 'homepage/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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
        context['attractions'] = Attraction.objects.filter(is_active=True)[:4]
        return context


class SustainabilityView(TemplateView):
    template_name = 'homepage/sustainability.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['policies'] = [
            {'title': 'Environmental Stewardship', 'icon': 'fa-leaf', 'desc': 'Energy-efficient LED lighting, solar water heating systems, and eco-conscious waste segregation.'},
            {'title': 'Responsible Water Management', 'icon': 'fa-droplet', 'desc': 'Water-saving shower fixtures, towel and bedsheet reuse request policies to reduce chemical detergent consumption.'},
            {'title': 'Local Organic Sourcing', 'icon': 'fa-wheat-awn', 'desc': 'Farm-to-table dining using fresh ingredients sourced directly from Nagarkot mountain farmers.'},
            {'title': 'Child & Community Protection', 'icon': 'fa-hand-holding-heart', 'desc': 'Zero tolerance for child labor, fair wages, employee health insurance, and local employment empowerment.'},
            {'title': 'Sustainable Architecture', 'icon': 'fa-building-columns', 'desc': 'Constructed with natural Newari bricks, handcrafted stone, and scrap wood furniture art.'},
            {'title': 'Quality & Safety Assurance', 'icon': 'fa-shield-halved', 'desc': 'Rigorous health & safety protocols across hotel rooms, kitchen gastronomy, and zipline operations.'}
        ]
        return context
