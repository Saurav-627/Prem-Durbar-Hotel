from django.contrib import admin
from django.contrib.admin import ModelAdmin
from .models.seo_data import SEOData

@admin.register(SEOData)
class SEODataAdmin(ModelAdmin):
    list_display = ('path', 'meta_title', 'meta_description')
    search_fields = ('path', 'meta_title', 'meta_description')

    fieldsets = (
        ("🔗 Page Identity", {
            "fields": ("path", "meta_title", "meta_description", "canonical_url"),
            "description": "Set the URL path and core SEO meta tags for this page.",
        }),
        ("🖼️ Banner Header", {
            "fields": ("header_subtitle", "header_title", "header_description", "header_image"),
            "description": (
                "Customize the hero banner shown at the top of the page. "
                "Leave blank to use the built-in default text and image."
            ),
        }),
        ("📣 Open Graph (OG) Tags", {
            "fields": ("og_title", "og_description", "og_image"),
            "classes": ("collapse",),
            "description": "Controls how this page appears when shared on Facebook, LinkedIn, etc.",
        }),
        ("🐦 Twitter Card", {
            "fields": ("twitter_card",),
            "classes": ("collapse",),
        }),
        ("⚙️ Structured Data (JSON-LD)", {
            "fields": ("structured_data",),
            "classes": ("collapse",),
            "description": "Paste raw JSON-LD schema markup here for rich search results.",
        }),
    )
