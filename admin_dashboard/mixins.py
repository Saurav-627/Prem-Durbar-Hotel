from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied

class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        # pyrefly: ignore [missing-attribute]
        user = self.request.user
        return user.is_authenticated and (user.is_staff or user.is_superuser or getattr(user, 'is_hotel_admin', False))

    # pyrefly: ignore [bad-override]
    def handle_no_permission(self):
        # pyrefly: ignore [missing-attribute]
        if not self.request.user.is_authenticated:
            return redirect('admin_dashboard:login')
        raise PermissionDenied("You do not have administrative access.")

def staff_required(view_func):
    def wrapper(request, *args, **kwargs):
        user = request.user
        if not (user.is_authenticated and (user.is_staff or user.is_superuser or getattr(user, 'is_hotel_admin', False))):
            if not user.is_authenticated:
                return redirect('admin_dashboard:login')
            raise PermissionDenied("You do not have administrative access.")
        return view_func(request, *args, **kwargs)
    return wrapper
