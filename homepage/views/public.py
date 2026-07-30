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
        
        # Clear stale search dates from session when landing on homepage
        self.request.session.pop('search_check_in', None)
        self.request.session.pop('search_check_out', None)
        
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
        
        # Zipline packages with multi-currency pricing
        from homepage.models.zipline_package import ZiplinePackage, ZiplinePackageBasePrice
        from homepage.models.zipline_cms import ZiplineCMS
        zipline_packages = list(ZiplinePackage.objects.filter(
            is_published=True
        ).prefetch_related(
            Prefetch(
                'base_prices',
                queryset=ZiplinePackageBasePrice.objects.filter(currency__iso_code=selected_currency),
                to_attr='active_currency_price'
            )
        ).order_by('order', 'id'))
        for pkg in zipline_packages:
            pkg.set_active_currency(selected_currency)
        context['zipline_packages'] = zipline_packages

        # Zipline CMS for homepage section (badge, heading, description)
        zipline_cms = ZiplineCMS.objects.first()
        if not zipline_cms:
            zipline_cms = ZiplineCMS.objects.create()
        context['zipline_cms'] = zipline_cms

        return context


from homepage.models import AboutPreview, AboutCMS, ZiplineCMS, SustainabilityCMS, SustainabilityPillar, TeamMember

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
        context['team_members'] = TeamMember.objects.filter(is_published=True).order_by('order', 'id')
        return context


class ZiplineView(TemplateView):
    template_name = 'homepage/zipline.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        zipline_cms = ZiplineCMS.objects.first()
        if not zipline_cms:
            zipline_cms = ZiplineCMS.objects.create()
        context['zipline_cms'] = zipline_cms

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

        from django.db.models import Prefetch
        from homepage.models.zipline_package import ZiplinePackage, ZiplinePackageBasePrice
        zipline_packages = list(ZiplinePackage.objects.filter(
            is_published=True
        ).prefetch_related(
            Prefetch(
                'base_prices',
                queryset=ZiplinePackageBasePrice.objects.filter(currency__iso_code=selected_currency),
                to_attr='active_currency_price'
            )
        ).order_by('order', 'id'))
        for pkg in zipline_packages:
            pkg.set_active_currency(selected_currency)
        context['zipline_packages'] = zipline_packages

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
