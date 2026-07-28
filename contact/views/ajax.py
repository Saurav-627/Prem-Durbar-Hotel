import re
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from ..models.inquiry import ContactInquiry

EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
PHONE_REGEX = r'^[\+]?[0-9\s\-\(\)]{7,20}$'

@require_POST
def submit_inquiry_ajax(request):
    name = request.POST.get('name', '').strip()
    email = request.POST.get('email', '').strip()
    phone = request.POST.get('phone', '').strip()
    subject = request.POST.get('subject', '').strip()
    message = request.POST.get('message', '').strip()
    category = request.POST.get('category', 'general')

    # Server-side Validation
    if not name or len(name) < 2:
        return HttpResponse(
            '<div class="p-4 bg-red-500/10 border border-red-500/30 text-red-700 dark:text-red-300 rounded-xl text-xs sm:text-sm font-semibold flex items-center gap-2.5 animate__animated animate__fadeIn">'
            '<i class="fa-solid fa-circle-exclamation text-red-500 text-base shrink-0"></i>'
            '<span>Please enter a valid full name (at least 2 characters).</span></div>',
            status=400
        )

    if not email or not re.match(EMAIL_REGEX, email):
        return HttpResponse(
            '<div class="p-4 bg-red-500/10 border border-red-500/30 text-red-700 dark:text-red-300 rounded-xl text-xs sm:text-sm font-semibold flex items-center gap-2.5 animate__animated animate__fadeIn">'
            '<i class="fa-solid fa-circle-exclamation text-red-500 text-base shrink-0"></i>'
            '<span>Please enter a valid email address (e.g. jane@example.com).</span></div>',
            status=400
        )

    if phone:
        digits = re.sub(r'\D', '', phone)
        if len(digits) != 10 or not re.match(r'^[\d\s().+-]+$', phone):
            return HttpResponse(
                '<div class="p-4 bg-red-500/10 border border-red-500/30 text-red-700 dark:text-red-300 rounded-xl text-xs sm:text-sm font-semibold flex items-center gap-2.5 animate__animated animate__fadeIn">'
                '<i class="fa-solid fa-circle-exclamation text-red-500 text-base shrink-0"></i>'
                '<span>Phone number must contain exactly 10 digits.</span></div>',
                status=400
            )

    if not subject or len(subject) < 3:
        return HttpResponse(
            '<div class="p-4 bg-red-500/10 border border-red-500/30 text-red-700 dark:text-red-300 rounded-xl text-xs sm:text-sm font-semibold flex items-center gap-2.5 animate__animated animate__fadeIn">'
            '<i class="fa-solid fa-circle-exclamation text-red-500 text-base shrink-0"></i>'
            '<span>Please enter a subject line with at least 3 characters.</span></div>',
            status=400
        )

    if not message or len(message) < 10:
        return HttpResponse(
            '<div class="p-4 bg-red-500/10 border border-red-500/30 text-red-700 dark:text-red-300 rounded-xl text-xs sm:text-sm font-semibold flex items-center gap-2.5 animate__animated animate__fadeIn">'
            '<i class="fa-solid fa-circle-exclamation text-red-500 text-base shrink-0"></i>'
            '<span>Please enter a detailed message (at least 10 characters).</span></div>',
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

    # Return success card & OOB toast notification
    return HttpResponse(
        f'<div class="p-5 bg-emerald-500/10 border border-emerald-500/30 text-emerald-800 dark:text-emerald-200 dark:bg-emerald-950/40 rounded-2xl animate__animated animate__fadeIn flex items-start gap-3 shadow-sm">'
        f'<div class="p-1 text-emerald-600 dark:text-emerald-400 text-xl flex-shrink-0 mt-0.5">'
        f'<i class="fa-solid fa-circle-check"></i>'
        f'</div>'
        f'<div class="space-y-1 text-xs sm:text-sm">'
        f'<h4 class="font-bold text-emerald-900 dark:text-emerald-100 text-sm sm:text-base">Message Sent Successfully</h4>'
        f'<p class="opacity-90 leading-relaxed">Thank you, <strong>{name}</strong>. Your inquiry about "<em>{subject}</em>" has been successfully logged. Our concierge desk will respond to you within 24 hours.</p>'
        f'</div>'
        f'</div>'
        f'<div id="toast-container" hx-swap-oob="afterbegin">'
        f'<div x-data="{{ show: true }}" x-show="show" x-init="setTimeout(() => show = false, 6000)" '
        f'class="p-4 rounded-xl shadow-2xl border border-emerald-500/30 bg-black/90 text-emerald-200 backdrop-blur-md flex items-start gap-3 pointer-events-auto animate__animated animate__fadeInRight">'
        f'<i class="fa-solid fa-circle-check text-emerald-400 text-lg flex-shrink-0 mt-0.5"></i>'
        f'<div class="flex-1 text-xs font-medium leading-relaxed">'
        f'<p class="font-bold text-white">Inquiry Sent!</p>'
        f'<p class="opacity-90">Your message has been received. We will be in touch shortly.</p>'
        f'</div>'
        f'<button @click="show = false" type="button" class="opacity-60 hover:opacity-100 transition-opacity">'
        f'<i class="fa-solid fa-xmark text-xs"></i>'
        f'</button>'
        f'</div>'
        f'</div>'
    )
