from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from ..models.branch import Branch
from ..models.category import ContactInquiryCategory
from ..models.newsletter import NewsletterSubscriber


class ContactView(TemplateView):
    template_name = 'contact/contact.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['branches'] = Branch.objects.filter(is_published=True).order_by('-is_main')
        context['inquiry_categories'] = ContactInquiryCategory.objects.filter(is_active=True).order_by('ordering', 'name')
        return context


@require_POST
def subscribe_newsletter(request):
    """
    Public endpoint for newsletter subscription.
    Handles AJAX (JSON response) and standard HTML form POSTs.
    """
    email = (request.POST.get('email') or '').strip().lower()

    if not email:
        msg = "Please provide a valid email address."
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
            return JsonResponse({'status': 'error', 'message': msg}, status=400)
        messages.error(request, msg)
        return redirect(request.META.get('HTTP_REFERER') or '/')

    try:
        validate_email(email)
    except ValidationError:
        msg = "Please enter a valid email address."
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
            return JsonResponse({'status': 'error', 'message': msg}, status=400)
        messages.error(request, msg)
        return redirect(request.META.get('HTTP_REFERER') or '/')

    subscriber, created = NewsletterSubscriber.objects.get_or_create(
        email=email,
        defaults={'is_active': True}
    )

    if not created and not subscriber.is_active:
        subscriber.is_active = True
        subscriber.save(update_fields=['is_active'])

    # Send Welcome Email via Mailpit / SMTP
    try:
        from payments.services.email_service import send_newsletter_welcome_email
        send_newsletter_welcome_email(email, request=request)
    except Exception:
        pass

    # Create Staff Admin Notification
    try:
        from admin_dashboard.models.notification import create_admin_notification
        from django.urls import reverse
        create_admin_notification(
            notification_type='inquiry_received',
            title='New Newsletter Subscriber',
            message=f"New guest subscribed to newsletter: {email}",
            link_url=reverse('admin_dashboard:contact_dashboard') + "?tab=subscribers"
        )
    except Exception:
        pass

    success_msg = "Thank you for subscribing to Prem Durbar newsletter!"
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
        return JsonResponse({'status': 'success', 'message': success_msg})

    messages.success(request, success_msg)
    return redirect(request.META.get('HTTP_REFERER') or '/')
