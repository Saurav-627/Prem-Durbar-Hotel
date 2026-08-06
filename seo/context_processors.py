import logging

from django.db.utils import OperationalError, ProgrammingError

from settings_manager.models.hotel_settings import HotelSettings

from .models.seo_data import SEOData


def seo_meta(request):
    site_name = 'Prem Durbar'
    try:
        hs = HotelSettings.objects.first()
        if hs and hs.site_name:
            site_name = hs.site_name
    except (ValueError, TypeError, KeyError, AttributeError, RuntimeError, OSError) as e:
        logging.getLogger(__name__).debug(f"Handled exception: {e}")

    meta = {
        'title': f'{site_name} | Premium Five-Star Luxury Hotel & CMS',
        'description': f'Experience ultimate luxury, fine dining, and elite wellness spas at {site_name}, a five-star international standard resort.',
        'canonical': request.build_absolute_uri(),
        'og_title': f'{site_name} | Five-Star Luxury Hotel',
        'og_description': 'Experience ultimate luxury, fine dining, and elite wellness spas.',
        'og_image': '',
        'twitter_card': 'summary_large_image',
        'structured_data': ''
    }

    # seo_obj: exact-path match, used for page banner header data (seo_raw)
    # meta_obj: may fall back to '/' for generic SEO meta tags
    seo_obj = None
    meta_obj = None

    try:
        # Exact match for current path — used for banner header data
        seo_obj = SEOData.objects.filter(path=request.path).first()

        # For meta tags, fall back to '/' record if no exact match
        meta_obj = seo_obj
        if not meta_obj and request.path != '/':
            meta_obj = SEOData.objects.filter(path='/').first()

        if meta_obj:
            meta['title'] = meta_obj.meta_title
            meta['description'] = meta_obj.meta_description
            meta['canonical'] = meta_obj.canonical_url or request.build_absolute_uri()
            meta['og_title'] = meta_obj.og_title or meta_obj.meta_title
            meta['og_description'] = meta_obj.og_description or meta_obj.meta_description
            if meta_obj.og_image:
                meta['og_image'] = request.build_absolute_uri(meta_obj.og_image.url)
            meta['twitter_card'] = meta_obj.twitter_card
            meta['structured_data'] = meta_obj.structured_data or ""
    except (ProgrammingError, OperationalError):
        pass

    return {'seo': meta, 'seo_raw': seo_obj}
