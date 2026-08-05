from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied

class StaffRequiredMixin(UserPassesTestMixin):
    permission_required = None

    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        
        # Superuser has full access
        if user.is_superuser:
            return True
            
        # User must have staff or hotel admin role
        if not (user.is_staff or getattr(user, 'is_hotel_admin', False)):
            return False
            
        # Check specific granular permission if required
        if self.permission_required:
            if isinstance(self.permission_required, (list, tuple)):
                return user.has_perms(self.permission_required)
            return user.has_perm(self.permission_required)
            
        return True

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect('admin_dashboard:login')
        raise PermissionDenied("You do not have the required permission to access this feature.")

def staff_required(permission=None):
    """Decorator for function-based views to enforce staff access and optional permission."""
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                return redirect('admin_dashboard:login')
            if user.is_superuser:
                return view_func(request, *args, **kwargs)
            if not (user.is_staff or getattr(user, 'is_hotel_admin', False)):
                raise PermissionDenied("You do not have administrative access.")
            if permission and not user.has_perm(permission):
                raise PermissionDenied("You do not have the required permission to perform this action.")
            return view_func(request, *args, **kwargs)
        return wrapper
    if callable(permission):
        func = permission
        permission = None
        return decorator(func)
    return decorator

