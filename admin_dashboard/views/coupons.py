from django.contrib import messages
from django.forms import inlineformset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import DeleteView, View

from admin_dashboard.forms import CouponForm, CouponMinSpendForm
from admin_dashboard.mixins import StaffRequiredMixin
from booking.models.coupon import Coupon, CouponMinSpend

MinSpendFormSet = inlineformset_factory(
    Coupon,
    CouponMinSpend,
    form=CouponMinSpendForm,
    fields=['currency', 'min_spend'],
    extra=3,
    can_delete=True,
    max_num=10,
)


class CouponDashboardView(StaffRequiredMixin, View):
    """List and manage all discount promo codes and coupons."""
    permission_required = 'booking.view_coupon'
    def get(self, request):
        from django.utils import timezone
        coupons = Coupon.objects.prefetch_related('min_spends__currency').order_by('-id')
        now = timezone.now()
        for c in coupons:
            # pyrefly: ignore [missing-attribute]
            c.is_expired_now = now > c.valid_to
        return render(request, 'admin_dashboard/coupons/dashboard.html', {
            'coupons': coupons,
        })


class CouponCreateView(StaffRequiredMixin, View):
    """Create a new promotional discount coupon code."""
    permission_required = 'booking.add_coupon'
    def get(self, request):
        form = CouponForm()
        min_spend_formset = MinSpendFormSet(prefix='min_spends')
        return render(request, 'admin_dashboard/coupons/coupon_form.html', {
            'form': form,
            'min_spend_formset': min_spend_formset,
            'title': 'Add New Promo / Coupon Code',
            'action_label': 'Create Coupon',
            'is_edit': False,
        })

    def post(self, request):
        form = CouponForm(request.POST)
        min_spend_formset = MinSpendFormSet(request.POST, prefix='min_spends')
        if form.is_valid() and min_spend_formset.is_valid():
            coupon = form.save()
            instances = min_spend_formset.save(commit=False)
            for obj in instances:
                obj.coupon = coupon
                obj.save()
            for obj in min_spend_formset.deleted_objects:
                obj.delete()
            messages.success(request, f"Promo code '{coupon.code}' created successfully.")
            return redirect(reverse('admin_dashboard:coupon_dashboard'))

        messages.error(request, "Error creating coupon. Please review highlighted inputs below.")
        return render(request, 'admin_dashboard/coupons/coupon_form.html', {
            'form': form,
            'min_spend_formset': min_spend_formset,
            'title': 'Add New Promo / Coupon Code',
            'action_label': 'Create Coupon',
            'is_edit': False,
        })


class CouponUpdateView(StaffRequiredMixin, View):
    """Edit an existing promo coupon code."""
    permission_required = 'booking.change_coupon'
    def get(self, request, pk):
        coupon = get_object_or_404(Coupon, pk=pk)
        form = CouponForm(instance=coupon)
        min_spend_formset = MinSpendFormSet(instance=coupon, prefix='min_spends')
        return render(request, 'admin_dashboard/coupons/coupon_form.html', {
            'form': form,
            'min_spend_formset': min_spend_formset,
            'title': f'Edit Promo Code: {coupon.code}',
            'action_label': 'Save Changes',
            'is_edit': True,
            'coupon': coupon,
        })

    def post(self, request, pk):
        coupon = get_object_or_404(Coupon, pk=pk)
        form = CouponForm(request.POST, instance=coupon)
        min_spend_formset = MinSpendFormSet(request.POST, instance=coupon, prefix='min_spends')
        if form.is_valid() and min_spend_formset.is_valid():
            coupon = form.save()
            instances = min_spend_formset.save(commit=False)
            for obj in instances:
                obj.coupon = coupon
                obj.save()
            for obj in min_spend_formset.deleted_objects:
                obj.delete()
            messages.success(request, f"Promo code '{coupon.code}' updated successfully.")
            return redirect(reverse('admin_dashboard:coupon_dashboard'))

        messages.error(request, "Error updating coupon. Please review highlighted inputs below.")
        return render(request, 'admin_dashboard/coupons/coupon_form.html', {
            'form': form,
            'min_spend_formset': min_spend_formset,
            'title': f'Edit Promo Code: {coupon.code}',
            'action_label': 'Save Changes',
            'is_edit': True,
            'coupon': coupon,
        })


class CouponDeleteView(StaffRequiredMixin, DeleteView):
    """Delete a promo code."""
    model = Coupon
    template_name = 'admin_dashboard/confirm_delete.html'
    permission_required = 'booking.delete_coupon'


    # pyrefly: ignore [bad-override]
    def get_success_url(self):
        messages.success(self.request, "Coupon deleted successfully.")
        return reverse_lazy('admin_dashboard:coupon_dashboard')
