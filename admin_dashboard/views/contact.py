from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages

from admin_dashboard.mixins import StaffRequiredMixin
from contact.models.branch import Branch
from contact.models.inquiry import ContactInquiry
from contact.models.category import ContactInquiryCategory
from contact.models.newsletter import NewsletterSubscriber
from admin_dashboard.forms import BranchForm, ContactInquiryCategoryForm, BroadcastNewsletterForm
from payments.services.email_service import send_newsletter_broadcast_email


from django.core.paginator import Paginator

class ContactDashboardView(StaffRequiredMixin, View):
    permission_required = 'contact.view_contactinquiry'
    def get(self, request):
        branches = Branch.objects.all()
        categories = ContactInquiryCategory.objects.all()
        active_tab = request.GET.get('tab', 'branches')
        page_number = request.GET.get('page', 1)

        # Inquiries Paginator (15 per page)
        inquiries_qs = ContactInquiry.objects.all().order_by('-created_at')
        inquiries_paginator = Paginator(inquiries_qs, 15)
        inquiries_page = inquiries_paginator.get_page(page_number if active_tab == 'inquiries' else 1)

        # Subscribers Paginator (15 per page)
        subscribers_qs = NewsletterSubscriber.objects.all().order_by('-created_at')
        subscribers_paginator = Paginator(subscribers_qs, 15)
        subscribers_page = subscribers_paginator.get_page(page_number if active_tab == 'subscribers' else 1)
        
        return render(request, 'admin_dashboard/contact/dashboard.html', {
            'branches': branches,
            'categories': categories,
            'inquiries': inquiries_page,
            'inquiries_total': inquiries_qs.count(),
            'subscribers': subscribers_page,
            'subscribers_total': subscribers_qs.count(),
            'active_tab': active_tab,
        })


class BroadcastNewsletterView(StaffRequiredMixin, View):
    permission_required = 'contact.add_newslettersubscriber'
    def get(self, request):
        form = BroadcastNewsletterForm()
        active_subscribers_count = NewsletterSubscriber.objects.filter(is_active=True).count()
        return render(request, 'admin_dashboard/contact/broadcast.html', {
            'form': form,
            'active_subscribers_count': active_subscribers_count,
        })

    def post(self, request):
        form = BroadcastNewsletterForm(request.POST)
        active_subscribers = list(NewsletterSubscriber.objects.filter(is_active=True).values_list('email', flat=True))
        
        if not active_subscribers:
            messages.error(request, "No active newsletter subscribers found to send broadcast.")
            return redirect(reverse_lazy('admin_dashboard:contact_dashboard') + "?tab=subscribers")

        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            
            success, sent_count, msg = send_newsletter_broadcast_email(
                subject=subject,
                message=message,
                recipient_list=active_subscribers,
                request=request
            )
            
            if success:
                messages.success(request, f"🚀 Campaign broadcasted successfully to {sent_count} active subscriber(s)!")
            else:
                messages.error(request, f"Failed to send campaign: {msg}")
            
            return redirect(reverse_lazy('admin_dashboard:contact_dashboard') + "?tab=subscribers")

        return render(request, 'admin_dashboard/contact/broadcast.html', {
            'form': form,
            'active_subscribers_count': len(active_subscribers),
        })


class NewsletterSubscriberToggleStatusView(StaffRequiredMixin, View):
    permission_required = 'contact.change_newslettersubscriber'
    def post(self, request, pk):
        subscriber = get_object_or_404(NewsletterSubscriber, pk=pk)
        subscriber.is_active = not subscriber.is_active
        subscriber.save(update_fields=['is_active'])
        
        status_text = "re-activated" if subscriber.is_active else "unsubscribed"
        messages.success(request, f"Subscriber {subscriber.email} has been {status_text}.")
        return redirect(reverse_lazy('admin_dashboard:contact_dashboard') + "?tab=subscribers")


class BranchCreateView(StaffRequiredMixin, CreateView):
    permission_required = 'contact.add_branch'
    model = Branch
    form_class = BranchForm
    template_name = 'admin_dashboard/generic_form.html'
    
    def get_success_url(self):
        messages.success(self.request, "Branch created successfully.")
        return reverse_lazy('admin_dashboard:contact_dashboard') + "?tab=branches"

class BranchUpdateView(StaffRequiredMixin, UpdateView):
    permission_required = 'contact.change_branch'
    model = Branch
    form_class = BranchForm
    template_name = 'admin_dashboard/generic_form.html'
    
    def get_success_url(self):
        messages.success(self.request, "Branch updated successfully.")
        return reverse_lazy('admin_dashboard:contact_dashboard') + "?tab=branches"

class BranchDeleteView(StaffRequiredMixin, DeleteView):
    permission_required = 'contact.delete_branch'
    model = Branch
    template_name = 'admin_dashboard/confirm_delete.html'
    
    def get_success_url(self):
        messages.success(self.request, "Branch deleted successfully.")
        return reverse_lazy('admin_dashboard:contact_dashboard') + "?tab=branches"

class ContactInquiryCategoryCreateView(StaffRequiredMixin, CreateView):
    permission_required = 'contact.add_contactinquirycategory'
    model = ContactInquiryCategory
    form_class = ContactInquiryCategoryForm
    template_name = 'admin_dashboard/generic_form.html'
    
    def get_success_url(self):
        messages.success(self.request, "Inquiry Category created successfully.")
        return reverse_lazy('admin_dashboard:contact_dashboard') + "?tab=categories"

class ContactInquiryCategoryUpdateView(StaffRequiredMixin, UpdateView):
    permission_required = 'contact.change_contactinquirycategory'
    model = ContactInquiryCategory
    form_class = ContactInquiryCategoryForm
    template_name = 'admin_dashboard/generic_form.html'
    
    def get_success_url(self):
        messages.success(self.request, "Inquiry Category updated successfully.")
        return reverse_lazy('admin_dashboard:contact_dashboard') + "?tab=categories"

class ContactInquiryCategoryDeleteView(StaffRequiredMixin, DeleteView):
    permission_required = 'contact.delete_contactinquirycategory'
    model = ContactInquiryCategory
    template_name = 'admin_dashboard/confirm_delete.html'
    
    def get_success_url(self):
        messages.success(self.request, "Inquiry Category deleted successfully.")
        return reverse_lazy('admin_dashboard:contact_dashboard') + "?tab=categories"

class ContactInquiryDetailView(StaffRequiredMixin, DetailView):
    permission_required = 'contact.view_contactinquiry'
    model = ContactInquiry
    template_name = 'admin_dashboard/contact/inquiry_detail.html'
    context_object_name = 'inquiry'

