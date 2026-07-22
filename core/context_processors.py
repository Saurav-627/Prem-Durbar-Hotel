from django.db.utils import ProgrammingError, OperationalError
from settings_manager.models.hotel_settings import HotelSettings
from settings_manager.models.navigation import NavigationMenu

def global_settings(request):
    # Safe defaults to prevent migration crashes
    settings_data = {
        'site_name': 'Prem Durbar',
        'theme': 'luxury',
        'contact_phone': '+977-1-4XXXXXX',
        'contact_email': 'info@hotelichchha.com',
        'address': 'Bara, Nepal',
        'about_text': 'A premium 5-star experience of hospitality and luxury.',
        'copyright_text': '&copy; 2026 Prem Durbar. All Rights Reserved.',
    }
    
    header_menu = []
    footer_quick_links = []
    footer_services = []
    footer_ota_links = []

    try:
        settings_obj = HotelSettings.objects.first()
        if settings_obj:
            settings_data = settings_obj
        else:
            # Create a default settings object if database is ready but empty
            settings_data = HotelSettings(
                site_name='Prem Durbar',
                theme='luxury',
                contact_phone='+977-1-4XXXXXX',
                contact_email='info@hotelichchha.com',
                address='Bara, Nepal',
                about_text='A premium 5-star experience of hospitality and luxury.'
            )

        # Retrieve menus
        from django.db.models import Prefetch
        menus = NavigationMenu.objects.filter(parent__isnull=True, is_published=True).prefetch_related(
            Prefetch('children', queryset=NavigationMenu.objects.filter(is_published=True))
        )
        header_menu = menus.filter(position='header')
        footer_quick_links = NavigationMenu.objects.filter(position='footer_links', is_published=True)
        footer_services = NavigationMenu.objects.filter(position='footer_services', is_published=True)
        footer_ota_links = NavigationMenu.objects.filter(position='footer_ota', is_published=True)
        
        # Retrieve active currencies
        from settings_manager.models.currency import Currency
        published_currencies = list(Currency.objects.filter(is_published=True))
        
        default_currency = 'USD'
        selected_currency = request.COOKIES.get('currency', default_currency)
        valid_codes = [c.iso_code for c in published_currencies]
        if selected_currency not in valid_codes:
            selected_currency = default_currency
            
        selected_theme = 'light'
        
    except (ProgrammingError, OperationalError):
        # Database tables do not exist yet (running migrations or setup)
        published_currencies = []
        selected_currency = 'USD'
        selected_theme = 'light'

    return {
        'hotel_settings': settings_data,
        'header_menu': header_menu,
        'footer_quick_links': footer_quick_links,
        'footer_services': footer_services,
        'footer_ota_links': footer_ota_links,
        'published_currencies': published_currencies,
        'selected_currency': selected_currency,
        'selected_theme': selected_theme,
    }
