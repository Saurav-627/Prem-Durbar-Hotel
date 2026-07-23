from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages

from admin_dashboard.mixins import StaffRequiredMixin
from homepage.models.hero_slide import HeroSlide
from homepage.models.about_preview import AboutPreview
from homepage.models.about_cms import AboutCMS
from homepage.models.zipline_cms import ZiplineCMS
from homepage.models.sustainability_cms import SustainabilityCMS, SustainabilityPillar
from testimonials.models.testimonial import Testimonial
from gallery.models.category import GalleryCategory
from gallery.models.item import GalleryItem
from seo.models.seo_data import SEOData

from admin_dashboard.forms import (
    HeroSlideForm, AboutPreviewForm, AboutCMSForm, ZiplineCMSForm, 
    SustainabilityCMSForm, SustainabilityPillarForm,
    TestimonialForm, GalleryCategoryForm, GalleryItemForm, SEODataForm
)

class CmsDashboardView(StaffRequiredMixin, View):
    def get(self, request):
        hero_slides = HeroSlide.objects.all()
        
        about_obj = AboutPreview.objects.first()
        if not about_obj:
            about_obj = AboutPreview.objects.create(content="A premium 5-star experience of hospitality and luxury.")
        about_form = AboutPreviewForm(instance=about_obj)

        about_cms_obj, _ = AboutCMS.objects.get_or_create(id=1)
        about_cms_form = AboutCMSForm(instance=about_cms_obj)

        zipline_cms_obj, _ = ZiplineCMS.objects.get_or_create(id=1)
        zipline_cms_form = ZiplineCMSForm(instance=zipline_cms_obj)

        sustainability_cms_obj, _ = SustainabilityCMS.objects.get_or_create(id=1)
        sustainability_cms_form = SustainabilityCMSForm(instance=sustainability_cms_obj)
        sustainability_pillars = SustainabilityPillar.objects.all()
        
        testimonials = Testimonial.objects.all()
        
        gallery_categories = GalleryCategory.objects.all()
        gallery_items = GalleryItem.objects.all().select_related('category')
        seo_data = SEOData.objects.all()
        
        active_tab = request.GET.get('tab', 'hero')
        
        return render(request, 'admin_dashboard/cms/dashboard.html', {
            'hero_slides': hero_slides,
            'about_form': about_form,
            'about_cms_form': about_cms_form,
            'zipline_cms_form': zipline_cms_form,
            'sustainability_cms_form': sustainability_cms_form,
            'sustainability_pillars': sustainability_pillars,
            'testimonials': testimonials,
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
        about_obj = AboutPreview.objects.first()
        if not about_obj:
            about_obj = AboutPreview.objects.create(content="A premium 5-star experience of hospitality and luxury.")
        form = AboutPreviewForm(request.POST, request.FILES, instance=about_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Homepage About preview updated successfully.")
        else:
            messages.error(request, "Error updating Homepage About preview.")
        return redirect(reverse_lazy('admin_dashboard:cms_dashboard') + "?tab=about")

# About Page CMS View
class AboutCMSUpdateView(StaffRequiredMixin, View):
    def post(self, request):
        obj, _ = AboutCMS.objects.get_or_create(id=1)
        form = AboutCMSForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "About page CMS content updated successfully.")
        else:
            messages.error(request, "Error updating About page CMS content.")
        return redirect(reverse_lazy('admin_dashboard:cms_dashboard') + "?tab=about_cms")

# Zipline Page CMS View
class ZiplineCMSUpdateView(StaffRequiredMixin, View):
    def post(self, request):
        obj, _ = ZiplineCMS.objects.get_or_create(id=1)
        form = ZiplineCMSForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Zipline page CMS content & video preview updated successfully.")
        else:
            messages.error(request, "Error updating Zipline page CMS content.")
        return redirect(reverse_lazy('admin_dashboard:cms_dashboard') + "?tab=zipline_cms")

# Sustainability Page CMS View
class SustainabilityCMSUpdateView(StaffRequiredMixin, View):
    def post(self, request):
        obj, _ = SustainabilityCMS.objects.get_or_create(id=1)
        form = SustainabilityCMSForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Sustainability page CMS content updated successfully.")
        else:
            messages.error(request, "Error updating Sustainability page CMS content.")
        return redirect(reverse_lazy('admin_dashboard:cms_dashboard') + "?tab=sustainability_cms")

class SustainabilityPillarCreateView(StaffRequiredMixin, CreateView):
    model = SustainabilityPillar
    form_class = SustainabilityPillarForm
    template_name = 'admin_dashboard/generic_form.html'
    
    def get_success_url(self):
        messages.success(self.request, "Sustainability pillar created successfully.")
        return reverse_lazy('admin_dashboard:cms_dashboard') + "?tab=sustainability_cms"

class SustainabilityPillarUpdateView(StaffRequiredMixin, UpdateView):
    model = SustainabilityPillar
    form_class = SustainabilityPillarForm
    template_name = 'admin_dashboard/generic_form.html'
    
    def get_success_url(self):
        messages.success(self.request, "Sustainability pillar updated successfully.")
        return reverse_lazy('admin_dashboard:cms_dashboard') + "?tab=sustainability_cms"

class SustainabilityPillarDeleteView(StaffRequiredMixin, DeleteView):
    model = SustainabilityPillar
    template_name = 'admin_dashboard/confirm_delete.html'
    
    def get_success_url(self):
        messages.success(self.request, "Sustainability pillar deleted successfully.")
        return reverse_lazy('admin_dashboard:cms_dashboard') + "?tab=sustainability_cms"

# Testimonial Views
class TestimonialCreateView(StaffRequiredMixin, CreateView):
    model = Testimonial
    form_class = TestimonialForm
    template_name = 'admin_dashboard/generic_form.html'
    
    def get_success_url(self):
        messages.success(self.request, "Testimonial created successfully.")
        return reverse_lazy('admin_dashboard:cms_dashboard') + "?tab=testimonials"

class TestimonialUpdateView(StaffRequiredMixin, UpdateView):
    model = Testimonial
    form_class = TestimonialForm
    template_name = 'admin_dashboard/generic_form.html'
    
    def get_success_url(self):
        messages.success(self.request, "Testimonial updated successfully.")
        return reverse_lazy('admin_dashboard:cms_dashboard') + "?tab=testimonials"

class TestimonialDeleteView(StaffRequiredMixin, DeleteView):
    model = Testimonial
    template_name = 'admin_dashboard/confirm_delete.html'
    
    def get_success_url(self):
        messages.success(self.request, "Testimonial deleted successfully.")
        return reverse_lazy('admin_dashboard:cms_dashboard') + "?tab=testimonials"

# Gallery Views
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

class GalleryItemCreateView(StaffRequiredMixin, CreateView):
    model = GalleryItem
    form_class = GalleryItemForm
    template_name = 'admin_dashboard/generic_form.html'
    
    def get_success_url(self):
        messages.success(self.request, "Gallery item added successfully.")
        return reverse_lazy('admin_dashboard:cms_dashboard') + "?tab=gallery"

class GalleryItemBulkUploadView(StaffRequiredMixin, View):
    def post(self, request):
        images = request.FILES.getlist('images')
        category_id = request.POST.get('category')
        category = get_object_or_404(GalleryCategory, pk=category_id) if category_id else None
        
        count = 0
        for img in images:
            GalleryItem.objects.create(category=category, image=img, title=img.name)
            count += 1
            
        messages.success(request, f"Successfully bulk uploaded {count} gallery image(s).")
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
        messages.success(self.request, "SEO record created successfully.")
        return reverse_lazy('admin_dashboard:cms_dashboard') + "?tab=seo"

class SeoUpdateView(StaffRequiredMixin, UpdateView):
    model = SEOData
    form_class = SEODataForm
    template_name = 'admin_dashboard/generic_form.html'
    
    def get_success_url(self):
        messages.success(self.request, "SEO record updated successfully.")
        return reverse_lazy('admin_dashboard:cms_dashboard') + "?tab=seo"

class SeoDeleteView(StaffRequiredMixin, DeleteView):
    model = SEOData
    template_name = 'admin_dashboard/confirm_delete.html'
    
    def get_success_url(self):
        messages.success(self.request, "SEO record deleted successfully.")
        return reverse_lazy('admin_dashboard:cms_dashboard') + "?tab=seo"

    
    def get_success_url(self):
        messages.success(self.request, "SEO record updated successfully.")
        return reverse_lazy('admin_dashboard:cms_dashboard') + "?tab=seo"
