from django.contrib import admin
from django.contrib.admin import ModelAdmin
from .models.testimonial import Testimonial

@admin.register(Testimonial)
class TestimonialAdmin(ModelAdmin):
    list_display = ('guest_name', 'source', 'rating', 'is_featured', 'is_published')
    list_filter = ('source', 'rating', 'is_featured', 'is_published')
    list_editable = ('is_featured', 'is_published')
    search_fields = ('guest_name', 'review_text')
