from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.forms import inlineformset_factory

from admin_dashboard.mixins import StaffRequiredMixin
from homepage.models.zipline_cms import ZiplineCMS
from homepage.models.zipline_package import ZiplinePackage, ZiplinePackageBasePrice
from admin_dashboard.forms import ZiplineCMSForm, ZiplinePackageForm, ZiplinePackageBasePriceForm

ZiplinePackageBasePriceFormSet = inlineformset_factory(
    ZiplinePackage, ZiplinePackageBasePrice, form=ZiplinePackageBasePriceForm,
    fields=('currency', 'base_price', 'discount_price'),
    extra=2, can_delete=True
)


class ZiplineDashboardView(StaffRequiredMixin, View):
    def get(self, request):
        zipline_cms_obj, _ = ZiplineCMS.objects.get_or_create(id=1)
        zipline_cms_form = ZiplineCMSForm(instance=zipline_cms_obj)
        zipline_packages = ZiplinePackage.objects.all().prefetch_related('base_prices__currency')
        active_tab = request.GET.get('tab', 'packages')

        return render(request, 'admin_dashboard/zipline/dashboard.html', {
            'zipline_cms_form': zipline_cms_form,
            'zipline_packages': zipline_packages,
            'active_tab': active_tab,
        })


class ZiplineCMSUpdateView(StaffRequiredMixin, View):
    def post(self, request):
        obj, _ = ZiplineCMS.objects.get_or_create(id=1)
        form = ZiplineCMSForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Zipline page CMS content & video preview updated successfully.")
            return redirect(reverse_lazy('admin_dashboard:zipline_dashboard') + "?tab=cms")
        else:
            err_msg = ", ".join([f"{k}: {v[0]}" for k, v in form.errors.items()])
            messages.error(request, f"Error updating Zipline page CMS content. Details: {err_msg}")
            zipline_packages = ZiplinePackage.objects.all().prefetch_related('base_prices__currency')
            return render(request, 'admin_dashboard/zipline/dashboard.html', {
                'zipline_cms_form': form,
                'zipline_packages': zipline_packages,
                'active_tab': 'cms',
            })


class ZiplinePackageCreateView(StaffRequiredMixin, View):
    def get(self, request):
        form = ZiplinePackageForm()
        currency_price_formset = ZiplinePackageBasePriceFormSet()
        return render(request, 'admin_dashboard/zipline/package_form.html', {
            'form': form,
            'currency_price_formset': currency_price_formset,
            'title': 'Add New Zipline Package'
        })

    def post(self, request):
        form = ZiplinePackageForm(request.POST, request.FILES)
        if form.is_valid():
            package = form.save()
            currency_price_formset = ZiplinePackageBasePriceFormSet(request.POST, instance=package)
            if currency_price_formset.is_valid():
                currency_price_formset.save()
                messages.success(request, "Zipline Package created successfully.")
                return redirect(reverse_lazy('admin_dashboard:zipline_dashboard') + "?tab=packages")
            else:
                package.delete()
                messages.error(request, "Error saving multi-currency prices. Please review the highlighted errors below.")
        else:
            currency_price_formset = ZiplinePackageBasePriceFormSet(request.POST)
            messages.error(request, "Error saving package details. Please review the highlighted errors below.")

        return render(request, 'admin_dashboard/zipline/package_form.html', {
            'form': form,
            'currency_price_formset': currency_price_formset,
            'title': 'Add New Zipline Package'
        })


class ZiplinePackageUpdateView(StaffRequiredMixin, View):
    def get(self, request, pk):
        package = get_object_or_404(ZiplinePackage, pk=pk)
        form = ZiplinePackageForm(instance=package)
        currency_price_formset = ZiplinePackageBasePriceFormSet(instance=package)
        return render(request, 'admin_dashboard/zipline/package_form.html', {
            'form': form,
            'currency_price_formset': currency_price_formset,
            'package': package,
            'title': f'Edit Zipline Package: {package.name}'
        })

    def post(self, request, pk):
        package = get_object_or_404(ZiplinePackage, pk=pk)
        form = ZiplinePackageForm(request.POST, request.FILES, instance=package)
        currency_price_formset = ZiplinePackageBasePriceFormSet(request.POST, instance=package)
        if form.is_valid() and currency_price_formset.is_valid():
            form.save()
            currency_price_formset.save()
            messages.success(request, "Zipline Package updated successfully.")
            return redirect(reverse_lazy('admin_dashboard:zipline_dashboard') + "?tab=packages")

        messages.error(request, "Error updating Zipline Package. Please review the highlighted errors below.")
        return render(request, 'admin_dashboard/zipline/package_form.html', {
            'form': form,
            'currency_price_formset': currency_price_formset,
            'package': package,
            'title': f'Edit Zipline Package: {package.name}'
        })


class ZiplinePackageDeleteView(StaffRequiredMixin, DeleteView):
    model = ZiplinePackage
    template_name = 'admin_dashboard/confirm_delete.html'

    def get_success_url(self):
        messages.success(self.request, "Zipline Package deleted successfully.")
        return reverse_lazy('admin_dashboard:zipline_dashboard') + "?tab=packages"
