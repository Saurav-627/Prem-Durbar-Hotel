from django.http import HttpResponse
from django.views.decorators.http import require_POST
from ..models.inquiry import ContactInquiry

@require_POST
def submit_inquiry_ajax(request):
    name = request.POST.get('name')
    email = request.POST.get('email')
    phone = request.POST.get('phone', '')
    subject = request.POST.get('subject')
    message = request.POST.get('message')
    category = request.POST.get('category', 'general')

    if not name or not email or not subject or not message:
        return HttpResponse(
            '<div class="p-4 bg-red-900/50 border border-red-500 text-red-200 rounded-lg">Please fill all required fields.</div>',
            status=400
        )

    # Save inquiry to database
    ContactInquiry.objects.create(
        name=name,
        email=email,
        phone=phone,
        subject=subject,
        message=message,
        category=category
    )

    # Trigger potential email notifications in background using Celery here if needed!

    return HttpResponse(
        f'<div class="p-5 bg-amber-900/40 border border-amber-500/50 text-amber-200 rounded-xl animate__animated animate__fadeIn">'
        f'<h4 class="font-semibold text-lg mb-1">Message Sent Successfully</h4>'
        f'<p class="text-sm opacity-90">Thank you, {name}. Your inquiry about "{subject}" has been successfully logged. Our concierge desk will respond to you within 24 hours.</p>'
        f'</div>'
    )
