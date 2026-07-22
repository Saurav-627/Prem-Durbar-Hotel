from django.shortcuts import render
from django.views.generic import View, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages

from admin_dashboard.mixins import StaffRequiredMixin
from contact.models.branch import Branch
from contact.models.inquiry import ContactInquiry
from admin_dashboard.forms import BranchForm

class ContactDashboardView(StaffRequiredMixin, View):
    def get(self, request):
        # pyrefly: ignore [missing-attribute]
        branches = Branch.objects.all()
        # pyrefly: ignore [missing-attribute]
        inquiries = ContactInquiry.objects.all()
        active_tab = request.GET.get('tab', 'branches')
        
        return render(request, 'admin_dashboard/contact/dashboard.html', {
            'branches': branches,
            'inquiries': inquiries,
            'active_tab': active_tab,
        })

class BranchCreateView(StaffRequiredMixin, CreateView):
    model = Branch
    form_class = BranchForm
    template_name = 'admin_dashboard/generic_form.html'
    
    def get_success_url(self):
        messages.success(self.request, "Branch created successfully.")
        return reverse_lazy('admin_dashboard:contact_dashboard') + "?tab=branches"

class BranchUpdateView(StaffRequiredMixin, UpdateView):
    model = Branch
    form_class = BranchForm
    template_name = 'admin_dashboard/generic_form.html'
    
    def get_success_url(self):
        messages.success(self.request, "Branch updated successfully.")
        return reverse_lazy('admin_dashboard:contact_dashboard') + "?tab=branches"

class BranchDeleteView(StaffRequiredMixin, DeleteView):
    model = Branch
    template_name = 'admin_dashboard/confirm_delete.html'
    
    def get_success_url(self):
        messages.success(self.request, "Branch deleted successfully.")
        return reverse_lazy('admin_dashboard:contact_dashboard') + "?tab=branches"

class ContactInquiryDetailView(StaffRequiredMixin, DetailView):
    model = ContactInquiry
    template_name = 'admin_dashboard/contact/inquiry_detail.html'
    context_object_name = 'inquiry'
