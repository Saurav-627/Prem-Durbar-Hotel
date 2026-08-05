import logging
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse

logger = logging.getLogger(__name__)


def send_booking_invoice_email(booking, payment=None, request=None):
    """
    Renders and dispatches an official HTML booking invoice email to the guest's email.
    Supports Mailpit and any configured Django SMTP backend.
    """
    if not booking.guest_email:
        logger.warning(f"Cannot send invoice email for Booking {booking.booking_uid}: No guest email provided.")
        return False, "No guest email provided."

    try:
        # Build absolute URL for online printable invoice receipt
        invoice_path = reverse('payments:view_invoice', kwargs={'booking_uid': booking.booking_uid})
        if request:
            invoice_url = request.build_absolute_uri(invoice_path)
        else:
            domain = getattr(settings, 'SITE_DOMAIN', '127.0.0.1:8000')
            protocol = 'http' if settings.DEBUG else 'https'
            invoice_url = f"{protocol}://{domain}{invoice_path}"

        # Fetch Hotel Settings for brand logo URL
        from settings_manager.models.hotel_settings import HotelSettings
        hotel_settings = HotelSettings.objects.first()
        logo_url = None
        if hotel_settings and hotel_settings.logo:
            logo_url = hotel_settings.logo.url
            if not logo_url.startswith('http'):
                if request:
                    logo_url = request.build_absolute_uri(logo_url)
                else:
                    domain = getattr(settings, 'SITE_DOMAIN', '127.0.0.1:8000')
                    protocol = 'http' if settings.DEBUG else 'https'
                    logo_url = f"{protocol}://{domain}{logo_url}"

        if not logo_url:
            static_logo = '/static/images/hotel-logo.png'
            if request:
                logo_url = request.build_absolute_uri(static_logo)
            else:
                domain = getattr(settings, 'SITE_DOMAIN', '127.0.0.1:8000')
                protocol = 'http' if settings.DEBUG else 'https'
                logo_url = f"{protocol}://{domain}{static_logo}"

        context = {
            'booking': booking,
            'payment': payment,
            'invoice_url': invoice_url,
            'logo_url': logo_url,
            'hotel_settings': hotel_settings,
        }

        # Render HTML body & fallback text body
        html_content = render_to_string('emails/booking_invoice_email.html', context)
            
        plain_content = strip_tags(html_content)

        subject = f"✓ Booking Invoice & Receipt [{booking.booking_uid}] — Prem Durbar Resort"
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'Prem Durbar Resort <noreply@premdurbar.com>')
        to_email = booking.guest_email

        msg = EmailMultiAlternatives(
            subject=subject,
            body=plain_content,
            from_email=from_email,
            to=[to_email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)

        logger.info(f"Successfully sent invoice email for Booking {booking.booking_uid} to {to_email}")
        return True, "Email sent successfully."

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Failed to send invoice email for Booking {booking.booking_uid} to {booking.guest_email}: {error_msg}")
        return False, error_msg


def send_newsletter_welcome_email(subscriber_email, request=None):
    """
    Renders and dispatches a welcome email to new newsletter subscribers.
    """
    if not subscriber_email:
        return False, "No subscriber email provided."

    try:
        from settings_manager.models.hotel_settings import HotelSettings
        hotel_settings = HotelSettings.objects.first()
        logo_url = None
        if hotel_settings and hotel_settings.logo:
            logo_url = hotel_settings.logo.url
            if not logo_url.startswith('http'):
                if request:
                    logo_url = request.build_absolute_uri(logo_url)
                else:
                    domain = getattr(settings, 'SITE_DOMAIN', '127.0.0.1:8000')
                    protocol = 'http' if settings.DEBUG else 'https'
                    logo_url = f"{protocol}://{domain}{logo_url}"

        if not logo_url:
            static_logo = '/static/images/hotel-logo.png'
            if request:
                logo_url = request.build_absolute_uri(static_logo)
            else:
                domain = getattr(settings, 'SITE_DOMAIN', '127.0.0.1:8000')
                protocol = 'http' if settings.DEBUG else 'https'
                logo_url = f"{protocol}://{domain}{static_logo}"

        if request:
            site_url = request.build_absolute_uri('/')
        else:
            domain = getattr(settings, 'SITE_DOMAIN', '127.0.0.1:8000')
            protocol = 'http' if settings.DEBUG else 'https'
            site_url = f"{protocol}://{domain}/"

        context = {
            'subscriber_email': subscriber_email,
            'logo_url': logo_url,
            'site_url': site_url,
            'hotel_settings': hotel_settings,
        }

        html_content = render_to_string('emails/newsletter_welcome_email.html', context)
        plain_content = strip_tags(html_content)

        site_name = hotel_settings.site_name if hotel_settings else "Prem Durbar Resort"
        subject = f"✨ Welcome to {site_name} — Exclusive Membership"
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'Prem Durbar Resort <noreply@premdurbar.com>')

        msg = EmailMultiAlternatives(
            subject=subject,
            body=plain_content,
            from_email=from_email,
            to=[subscriber_email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)

        logger.info(f"Successfully sent newsletter welcome email to {subscriber_email}")
        return True, "Welcome email sent."

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Failed to send newsletter welcome email to {subscriber_email}: {error_msg}")
        return False, error_msg


def send_newsletter_verification_email(subscriber, verification_url, request=None):
    """
    Renders and dispatches a double opt-in email verification email to new subscribers.
    """
    if not subscriber or not subscriber.email:
        return False, "No subscriber email provided."

    try:
        from settings_manager.models.hotel_settings import HotelSettings
        hotel_settings = HotelSettings.objects.first()
        logo_url = None
        if hotel_settings and hotel_settings.logo:
            logo_url = hotel_settings.logo.url
            if not logo_url.startswith('http'):
                if request:
                    logo_url = request.build_absolute_uri(logo_url)
                else:
                    domain = getattr(settings, 'SITE_DOMAIN', '127.0.0.1:8000')
                    protocol = 'http' if settings.DEBUG else 'https'
                    logo_url = f"{protocol}://{domain}{logo_url}"

        if not logo_url:
            static_logo = '/static/images/hotel-logo.png'
            if request:
                logo_url = request.build_absolute_uri(static_logo)
            else:
                domain = getattr(settings, 'SITE_DOMAIN', '127.0.0.1:8000')
                protocol = 'http' if settings.DEBUG else 'https'
                logo_url = f"{protocol}://{domain}{static_logo}"

        if request:
            site_url = request.build_absolute_uri('/')
        else:
            domain = getattr(settings, 'SITE_DOMAIN', '127.0.0.1:8000')
            protocol = 'http' if settings.DEBUG else 'https'
            site_url = f"{protocol}://{domain}/"

        context = {
            'subscriber_email': subscriber.email,
            'verification_url': verification_url,
            'logo_url': logo_url,
            'site_url': site_url,
            'hotel_settings': hotel_settings,
        }

        html_content = render_to_string('emails/newsletter_verification_email.html', context)
        plain_content = strip_tags(html_content)

        site_name = hotel_settings.site_name if hotel_settings else "Prem Durbar Resort"
        subject = f"✉️ Please Confirm Your Newsletter Subscription — {site_name}"
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'Prem Durbar Resort <noreply@premdurbar.com>')

        msg = EmailMultiAlternatives(
            subject=subject,
            body=plain_content,
            from_email=from_email,
            to=[subscriber.email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)

        logger.info(f"Successfully sent newsletter verification email to {subscriber.email}")
        return True, "Verification email sent."

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Failed to send newsletter verification email to {subscriber.email}: {error_msg}")
        return False, error_msg


def send_newsletter_broadcast_email(subject, message, recipient_list, request=None):
    """
    Renders and dispatches a bulk newsletter broadcast email to all active subscriber emails.
    """
    if not recipient_list:
        return False, 0, "No active recipient emails provided."

    try:
        from settings_manager.models.hotel_settings import HotelSettings
        hotel_settings = HotelSettings.objects.first()
        logo_url = None
        if hotel_settings and hotel_settings.logo:
            logo_url = hotel_settings.logo.url
            if not logo_url.startswith('http'):
                if request:
                    logo_url = request.build_absolute_uri(logo_url)
                else:
                    domain = getattr(settings, 'SITE_DOMAIN', '127.0.0.1:8000')
                    protocol = 'http' if settings.DEBUG else 'https'
                    logo_url = f"{protocol}://{domain}{logo_url}"

        if not logo_url:
            static_logo = '/static/images/hotel-logo.png'
            if request:
                logo_url = request.build_absolute_uri(static_logo)
            else:
                domain = getattr(settings, 'SITE_DOMAIN', '127.0.0.1:8000')
                protocol = 'http' if settings.DEBUG else 'https'
                logo_url = f"{protocol}://{domain}{static_logo}"

        if request:
            site_url = request.build_absolute_uri('/')
        else:
            domain = getattr(settings, 'SITE_DOMAIN', '127.0.0.1:8000')
            protocol = 'http' if settings.DEBUG else 'https'
            site_url = f"{protocol}://{domain}/"

        context = {
            'subject': subject,
            'message': message,
            'logo_url': logo_url,
            'site_url': site_url,
            'hotel_settings': hotel_settings,
        }

        html_content = render_to_string('emails/newsletter_broadcast_email.html', context)
        plain_content = strip_tags(html_content)
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'Prem Durbar Resort <noreply@premdurbar.com>')

        sent_count = 0
        for email in recipient_list:
            try:
                msg = EmailMultiAlternatives(
                    subject=subject,
                    body=plain_content,
                    from_email=from_email,
                    to=[email]
                )
                msg.attach_alternative(html_content, "text/html")
                msg.send(fail_silently=False)
                sent_count += 1
            except Exception as item_err:
                logger.error(f"Error sending campaign email to {email}: {item_err}")

        logger.info(f"Successfully broadcasted campaign '{subject}' to {sent_count}/{len(recipient_list)} subscribers.")
        return True, sent_count, f"Campaign sent to {sent_count} subscribers."

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Failed to execute broadcast email: {error_msg}")
        return False, 0, error_msg
