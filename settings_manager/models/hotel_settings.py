from django.db import models
from core.utils import UploadTo, ValidateFileSize

class HotelSettings(models.Model):
    THEME_CHOICES = [
        ('light', 'Light Mode'),
        ('dark', 'Dark Mode'),
        ('luxury', 'Luxury Gold Mode'),
        ('festival', 'Festival Theme'),
    ]

    site_name = models.CharField(max_length=100, default="Prem Durbar")
    favicon = models.ImageField(
        upload_to=UploadTo('settings/favicons'),
        blank=True,
        null=True,
        help_text="Browser favicon icon (.png, .ico, .svg)",
        validators=[ValidateFileSize(2)]
    )
    logo = models.ImageField(
        upload_to=UploadTo('settings/logos'),
        blank=True,
        null=True,
        validators=[ValidateFileSize(2)]
    )
    logo_dark = models.ImageField(
        upload_to=UploadTo('settings/logos'),
        blank=True,
        null=True,
        help_text="Dark mode logo version",
        validators=[ValidateFileSize(2)]
    )
    admin_logo = models.ImageField(
        upload_to=UploadTo('settings/logos'),
        blank=True,
        null=True,
        help_text="Admin panel logo (falls back to main logo if blank)",
        validators=[ValidateFileSize(2)]
    )
    admin_title = models.CharField(
        max_length=100,
        default="Prem Durbar CMS Admin Dashboard",
        help_text="Admin panel browser tab title"
    )
    admin_label = models.CharField(
        max_length=100,
        default="Prem Durbar Portal",
        help_text="Admin sidebar header label"
    )
    theme = models.CharField(max_length=20, choices=THEME_CHOICES, default='luxury')
    
    # Contact Info & Company VAT Details
    contact_phone = models.CharField(max_length=50, default="+977-015145351, +977-9851160380")
    contact_email = models.EmailField(default="info@premdurbar.com")
    address = models.CharField(max_length=255, default="Nagarkot, Nepal")
    vat_no = models.CharField(max_length=50, default="609554676", help_text="Company VAT/PAN Registration Number")
    
    # Official Zipline Entity Details
    zipline_company_name = models.CharField(max_length=150, default="NAGARKOT ZIPLINE PVT. LTD", help_text="Official registered name of zipline company")
    zipline_address = models.CharField(max_length=255, default="Chagunarayan-07, Bhaktapur, Nepal", help_text="Registered address of zipline company")
    zipline_phone = models.CharField(max_length=100, default="+977-015145351, +977-9851160380", help_text="Official zipline contact phone numbers")
    google_maps_iframe = models.TextField(blank=True, null=True, help_text="Google Maps HTML embed iframe")

    # Social Links
    facebook_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    youtube_url = models.URLField(blank=True, null=True)
    tripadvisor_url = models.URLField(blank=True, null=True)

    # Header CTA & Banner Settings
    header_cta_text = models.CharField(max_length=100, default="Book A Stay", help_text="Text shown on header CTA button")
    header_cta_url = models.CharField(max_length=255, default="/rooms/", help_text="Link URL for header CTA button")

    # Footer details & Payment Icons
    about_text = models.TextField(default="A premium 5-star experience of hospitality and luxury.")
    copyright_text = models.CharField(max_length=255, default="&copy; 2026 Prem Durbar. All Rights Reserved.")
    footer_awards_text = models.CharField(max_length=255, default="Powered by PocketSoft Pvt Ltd", help_text="Footer credits badge text (e.g. Powered by PocketSoft Pvt Ltd)")
    footer_credits_url = models.CharField(max_length=255, default="", blank=True, null=True, help_text="Link URL for footer credits badge (optional)")
    
    footer_show_visa = models.BooleanField(default=True, help_text="Display Visa logo in footer")
    footer_show_mastercard = models.BooleanField(default=True, help_text="Display Mastercard logo in footer")
    footer_show_stripe = models.BooleanField(default=True, help_text="Display Stripe logo in footer")
    footer_show_esewa = models.BooleanField(default=True, help_text="Display eSewa logo in footer")
    footer_show_khalti = models.BooleanField(default=True, help_text="Display Khalti logo in footer")

    # Mobile Menu Drawer CTA Settings
    mobile_menu_cta_text = models.CharField(max_length=100, default="Book A Stay", help_text="Text shown on mobile menu CTA button")
    mobile_menu_cta_url = models.CharField(max_length=255, default="/rooms/", help_text="Link URL for mobile menu CTA button")

    # Search Modal Overlay Strings
    search_modal_title = models.CharField(max_length=150, default="Search Resort", help_text="Title shown in search overlay modal")
    search_modal_placeholder = models.CharField(max_length=255, default="Search room categories, dining, amenities...", help_text="Placeholder text in search input")
    search_modal_button_text = models.CharField(max_length=50, default="Search", help_text="Button text in search modal")

    # Homepage Section Headings & Subtitles
    rooms_section_subtitle = models.CharField(max_length=150, default="Premium Sanctuary")
    rooms_section_title = models.CharField(max_length=150, default="Rooms & Suites")
    rooms_section_desc = models.TextField(default="Explore our signature guest chambers designed for ultimate relaxation and comfort.")

    facilities_section_subtitle = models.CharField(max_length=150, default="Elite Hospitality")
    facilities_section_title = models.CharField(max_length=150, default="Resort Services & Facilities")
    facilities_section_desc = models.TextField(default="Indulge in our carefully curated amenities, designed to elevate your stay to a world-class level.")

    testimonials_section_subtitle = models.CharField(max_length=150, default="Guest Memoirs")
    testimonials_section_title = models.CharField(max_length=150, default="What Our Guests Say")

    newsletter_section_subtitle = models.CharField(max_length=150, default="Newsletter Subscription")
    newsletter_section_title = models.CharField(max_length=150, default="Join The Elite Guild")
    newsletter_section_desc = models.TextField(default="Subscribe to receive exclusive offers, luxury travel logs, seasonal booking discounts, and resort news.")
    newsletter_btn_text = models.CharField(max_length=50, default="Subscribe")

    class Meta:
        verbose_name = "Hotel Global Settings"
        verbose_name_plural = "Hotel Global Settings"

    def __str__(self):
        return f"{self.site_name} Settings"

    def save(self, *args, **kwargs):
        # Override save to ensure only one instance of HotelSettings exists
        if not self.pk and HotelSettings.objects.exists():
            # If dynamic save occurs, replace the existing one
            # pyrefly: ignore [missing-attribute]
            self.pk = HotelSettings.objects.first().pk
        super().save(*args, **kwargs)
