import secrets
from django.views.generic import TemplateView
from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.urls import reverse

from ..models.branch import Branch
from ..models.category import ContactInquiryCategory
from ..models.newsletter import NewsletterSubscriber
from core.services.email_service import send_newsletter_welcome_email
from core.services.email_service import send_newsletter_verification_email


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
    Public endpoint for newsletter double opt-in subscription.
    Sends verification email link to the subscriber before activating.
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
        email=email
    )

    if subscriber.is_verified and subscriber.is_active:
        info_msg = "You are already a verified subscriber to our newsletter!"
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
            return JsonResponse({'status': 'info', 'message': info_msg})
        messages.info(request, info_msg)
        return redirect(request.META.get('HTTP_REFERER') or '/')

    # Generate verification token
    token = secrets.token_urlsafe(32)
    subscriber.verification_token = token
    subscriber.is_verified = False
    subscriber.is_active = False
    subscriber.save()

    # Build Verification Link URL
    verification_url = request.build_absolute_uri(reverse('contact:verify_newsletter', args=[token]))

    # Send Verification Email via Mailpit / SMTP
    try:
        send_newsletter_verification_email(subscriber, verification_url, request=request)
    except Exception:
        pass

    success_msg = "✉️ A verification link has been sent to your email. Please check your inbox to confirm your subscription."
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
        return JsonResponse({'status': 'success', 'message': success_msg})

    messages.success(request, success_msg)
    return redirect(request.META.get('HTTP_REFERER') or '/')


def verify_newsletter(request, token):
    """
    Verification endpoint triggered when user clicks confirmation link in email.
    """
    subscriber = NewsletterSubscriber.objects.filter(verification_token=token).first()

    if not subscriber:
        messages.error(request, "Invalid or expired newsletter verification link.")
        return redirect('/')

    # Mark as verified and active
    subscriber.is_verified = True
    subscriber.is_active = True
    subscriber.verification_token = None
    subscriber.save()

    # Send Welcome Email
    try:
        send_newsletter_welcome_email(subscriber.email, request=request)
    except Exception:
        pass

    # Create Staff Admin Notification
    try:
        from admin_dashboard.models.notification import create_admin_notification
        create_admin_notification(
            notification_type='inquiry_received',
            title='Verified Newsletter Subscriber',
            message=f"New guest verified newsletter subscription: {subscriber.email}",
            link_url=reverse('admin_dashboard:contact_dashboard') + "?tab=subscribers"
        )
    except Exception:
        pass

    messages.success(request, "🎉 Your email has been verified successfully! Welcome to the Prem Durbar newsletter.")
    return redirect('/')
