from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages

from admin_dashboard.mixins import StaffRequiredMixin
from homepage.models.hero_slide import HeroSlide
from homepage.models.about_preview import AboutPreview
from testimonials.models.testimonial import Testimonial
from nearby_places.models.attraction import Attraction
from gallery.models.category import GalleryCategory
from gallery.models.item import GalleryItem
from seo.models.seo_data import SEOData

from admin_dashboard.forms import (
    HeroSlideForm, AboutPreviewForm, TestimonialForm, 
    AttractionForm, GalleryCategoryForm, GalleryItemForm, SEODataForm
)

class CmsDashboardView(StaffRequiredMixin, View):
    def get(self, request):
        hero_slides = HeroSlide.objects.all()
        
        about_obj = AboutPreview.objects.first()
        if not about_obj:
            about_obj = AboutPreview.objects.create(content="A premium 5-star experience of hospitality and luxury.")
        about_form = AboutPreviewForm(instance=about_obj)
        
        testimonials = Testimonial.objects.all()
        attractions = Attraction.objects.all()
        
        gallery_categories = GalleryCategory.objects.all()
        gallery_items = GalleryItem.objects.all().select_related('category')
        seo_data = SEOData.objects.all()
        
        active_tab = request.GET.get('tab', 'hero')
        
        return render(request, 'admin_dashboard/cms/dashboard.html', {
            'hero_slides': hero_slides,
            'about_form': about_form,
            'testimonials': testimonials,
            'attractions': attractions,
            'gallery_categories': gallery_categories,
            'gallery_items': gallery_items,
            'seo_data': seo_data,
            'active_tab': active_tab,
        })

# Hero Slide Views
class HeroSlideCreateView(StaffRequiredMixin, CreateView):
    model = HeroSlide
    form_class = HeroSlideForm
    template_name = 'admin_dashboard/generic_form.html'
    
    def get_success_url(self):
        messages.success(self.request, "Hero slide created successfully.")
        return reverse_lazy('admin_dashboard:cms_dashboard') + "?tab=hero"

class HeroSlideUpdateView(StaffRequiredMixin, UpdateView):
    model = HeroSlide
    form_class = HeroSlideForm
    template_name = 'admin_dashboard/generic_form.html'
    
    def get_success_url(self):
        messages.success(self.request, "Hero slide updated successfully.")
        return reverse_lazy('admin_dashboard:cms_dashboard') + "?tab=hero"

class HeroSlideDeleteView(StaffRequiredMixin, DeleteView):
    model = HeroSlide
    template_name = 'admin_dashboard/confirm_delete.html'
    
    def get_success_url(self):
        messages.success(self.request, "Hero slide deleted successfully.")
        return reverse_lazy('admin_dashboard:cms_dashboard') + "?tab=hero"

# About Preview singleton
class AboutPreviewUpdateView(StaffRequiredMixin, View):
    def post(self, request):
        # pyrefly: ignore [missing-attribute]
        about_obj = AboutPreview.objects.first()
        if not about_obj:
            # pyrefly: ignore [missing-attribute]
            about_obj = AboutPreview.objects.create(content="A premium 5-star experience of hospitality and luxury.")
            
        form = AboutPreviewForm(request.POST, request.FILES, instance=about_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Homepage About Preview updated successfully.")
        else:
            messages.error(request, "Failed to update About Preview. Please verify details.")
        return redirect(reverse_lazy('admin_dashboard:cms_dashboard') + "?tab=about")

# Testimonial Views
class TestimonialCreateView(StaffRequiredMixin, CreateView):
    model = Testimonial
    form_class = TestimonialForm
    template_name = 'admin_dashboard/generic_form.html'
    
    def get_success_url(self):
        messages.success(self.request, "Testimonial review created successfully.")
        return reverse_lazy('admin_dashboard:cms_dashboard') + "?tab=testimonials"

class TestimonialUpdateView(StaffRequiredMixin, UpdateView):
    model = Testimonial
    form_class = TestimonialForm
    template_name = 'admin_dashboard/generic_form.html'
    
    def get_success_url(self):
        messages.success(self.request, "Testimonial review updated successfully.")
        return reverse_lazy('admin_dashboard:cms_dashboard') + "?tab=testimonials"

class TestimonialDeleteView(StaffRequiredMixin, DeleteView):
    model = Testimonial
    template_name = 'admin_dashboard/confirm_delete.html'
    
    def get_success_url(self):
        messages.success(self.request, "Testimonial review deleted successfully.")
        return reverse_lazy('admin_dashboard:cms_dashboard') + "?tab=testimonials"

# Nearby Attractions Views
class AttractionCreateView(StaffRequiredMixin, CreateView):
    model = Attraction
    form_class = AttractionForm
    template_name = 'admin_dashboard/generic_form.html'
    
    def get_success_url(self):
        messages.success(self.request, "Nearby attraction created successfully.")
        return reverse_lazy('admin_dashboard:cms_dashboard') + "?tab=nearby"

class AttractionUpdateView(StaffRequiredMixin, UpdateView):
    model = Attraction
    form_class = AttractionForm
    template_name = 'admin_dashboard/generic_form.html'
    
    def get_success_url(self):
        messages.success(self.request, "Nearby attraction updated successfully.")
        return reverse_lazy('admin_dashboard:cms_dashboard') + "?tab=nearby"

class AttractionDeleteView(StaffRequiredMixin, DeleteView):
    model = Attraction
    template_name = 'admin_dashboard/confirm_delete.html'
    
    def get_success_url(self):
        messages.success(self.request, "Nearby attraction deleted successfully.")
        return reverse_lazy('admin_dashboard:cms_dashboard') + "?tab=nearby"

# Gallery Views
class GalleryItemCreateView(StaffRequiredMixin, CreateView):
    model = GalleryItem
    form_class = GalleryItemForm
    template_name = 'admin_dashboard/generic_form.html'
    
    def get_success_url(self):
        messages.success(self.request, "Gallery item uploaded successfully.")
        return reverse_lazy('admin_dashboard:cms_dashboard') + "?tab=gallery"

class GalleryItemBulkUploadView(StaffRequiredMixin, View):
    def post(self, request):
        category_id = request.POST.get('category')
        files = request.FILES.getlist('images')
        
        if not category_id:
            messages.error(request, "Please select a gallery category.")
            return redirect(reverse_lazy('admin_dashboard:cms_dashboard') + "?tab=gallery")
            
        category = get_object_or_404(GalleryCategory, id=category_id)
        
        if not files:
            messages.warning(request, "No files selected for upload.")
            return redirect(reverse_lazy('admin_dashboard:cms_dashboard') + "?tab=gallery")
            
        count = 0
        for f in files:
            # pyrefly: ignore [missing-attribute]
            GalleryItem.objects.create(
                category=category,
                image=f,
                is_published=True
            )
            count += 1
            
        messages.success(request, f"Successfully uploaded {count} image(s) to {category.name}.")
        return redirect(reverse_lazy('admin_dashboard:cms_dashboard') + "?tab=gallery")

class GalleryItemDeleteView(StaffRequiredMixin, DeleteView):
    model = GalleryItem
    template_name = 'admin_dashboard/confirm_delete.html'
    
    def get_success_url(self):
        messages.success(self.request, "Gallery item deleted successfully.")
        return reverse_lazy('admin_dashboard:cms_dashboard') + "?tab=gallery"

# SEO Views
class SeoCreateView(StaffRequiredMixin, CreateView):
    model = SEOData
    form_class = SEODataForm
    template_name = 'admin_dashboard/generic_form.html'
    
    def get_success_url(self):
        messages.success(self.request, "SEO settings page created successfully.")
        return reverse_lazy('admin_dashboard:cms_dashboard') + "?tab=seo"

class SeoUpdateView(StaffRequiredMixin, UpdateView):
    model = SEOData
    form_class = SEODataForm
    template_name = 'admin_dashboard/generic_form.html'
    
    def get_success_url(self):
        messages.success(self.request, "SEO settings page updated successfully.")
        return reverse_lazy('admin_dashboard:cms_dashboard') + "?tab=seo"

class SeoDeleteView(StaffRequiredMixin, DeleteView):
    model = SEOData
    template_name = 'admin_dashboard/confirm_delete.html'
    
    def get_success_url(self):
        messages.success(self.request, "SEO settings page deleted successfully.")
        return reverse_lazy('admin_dashboard:cms_dashboard') + "?tab=seo"


# Gallery Category Views
class GalleryCategoryCreateView(StaffRequiredMixin, CreateView):
    model = GalleryCategory
    form_class = GalleryCategoryForm
    template_name = 'admin_dashboard/generic_form.html'
    
    def get_success_url(self):
        messages.success(self.request, "Gallery category created successfully.")
        return reverse_lazy('admin_dashboard:cms_dashboard') + "?tab=gallery"

class GalleryCategoryUpdateView(StaffRequiredMixin, UpdateView):
    model = GalleryCategory
    form_class = GalleryCategoryForm
    template_name = 'admin_dashboard/generic_form.html'
    
    def get_success_url(self):
        messages.success(self.request, "Gallery category updated successfully.")
        return reverse_lazy('admin_dashboard:cms_dashboard') + "?tab=gallery"

class GalleryCategoryDeleteView(StaffRequiredMixin, DeleteView):
    model = GalleryCategory
    template_name = 'admin_dashboard/confirm_delete.html'
    
    def get_success_url(self):
        messages.success(self.request, "Gallery category deleted successfully.")
        return reverse_lazy('admin_dashboard:cms_dashboard') + "?tab=gallery"
