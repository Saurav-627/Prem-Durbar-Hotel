from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.views.generic import ListView

from ..mixins import StaffRequiredMixin
from ..models.notification import Notification


class NotificationListView(StaffRequiredMixin, ListView):
    model = Notification
    template_name = 'admin_dashboard/notifications/list.html'
    context_object_name = 'notifications'
    paginate_by = 20

    def get_queryset(self):
        qs = Notification.objects.all()
        status_filter = self.request.GET.get('status')
        if status_filter == 'unread':
            qs = qs.filter(is_read=False)
        elif status_filter == 'read':
            qs = qs.filter(is_read=True)
        return qs


@require_POST
def mark_notification_read(request, pk):
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
    
    notification = get_object_or_404(Notification, pk=pk)
    notification.is_read = True
    notification.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
        return JsonResponse({'status': 'success', 'unread_count': Notification.objects.filter(is_read=False).count()})

    next_url = request.POST.get('next') or notification.link_url or request.META.get('HTTP_REFERER') or 'admin_dashboard:notification_list'
    return redirect(next_url)


@require_POST
def mark_all_notifications_read(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)

    Notification.objects.filter(is_read=False).update(is_read=True)
    messages.success(request, "All notifications marked as read.")

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
        return JsonResponse({'status': 'success', 'unread_count': 0})

    return redirect(request.META.get('HTTP_REFERER') or 'admin_dashboard:notification_list')
