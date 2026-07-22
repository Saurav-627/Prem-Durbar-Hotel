from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Q

from admin_dashboard.mixins import StaffRequiredMixin
from admin_dashboard.forms import UserForm

User = get_user_model()

class UserListView(StaffRequiredMixin, ListView):
    model = User
    template_name = 'admin_dashboard/users/list.html'
    context_object_name = 'users'
    paginate_by = 15

    def get_queryset(self):
        queryset = User.objects.all().order_by('-date_joined')
        
        # Search query
        q = self.request.GET.get('search', '').strip()
        if q:
            queryset = queryset.filter(
                # pyrefly: ignore [unsupported-operation]
                Q(username__icontains=q) |
                Q(email__icontains=q) |
                Q(phone__icontains=q) |
                Q(first_name__icontains=q) |
                Q(last_name__icontains=q)
            )
            
        # Role filtering
        role = self.request.GET.get('role', '').strip()
        if role == 'staff':
            # pyrefly: ignore [unsupported-operation]
            queryset = queryset.filter(Q(is_staff=True) | Q(is_superuser=True) | Q(is_hotel_admin=True))
        elif role == 'guest':
            queryset = queryset.filter(is_guest=True)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_role'] = self.request.GET.get('role', '')
        context['search_query'] = self.request.GET.get('search', '')
        return context

class UserCreateView(StaffRequiredMixin, CreateView):
    model = User
    form_class = UserForm
    template_name = 'admin_dashboard/generic_form.html'
    success_url = reverse_lazy('admin_dashboard:user_list')
    
    def get_success_url(self):
        messages.success(self.request, "User created successfully.")
        return reverse('admin_dashboard:user_list')

class UserUpdateView(StaffRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'admin_dashboard/generic_form.html'
    success_url = reverse_lazy('admin_dashboard:user_list')
    
    def get_success_url(self):
        messages.success(self.request, "User details updated successfully.")
        return reverse('admin_dashboard:user_list')

class UserDeleteView(StaffRequiredMixin, DeleteView):
    model = User
    template_name = 'admin_dashboard/confirm_delete.html'
    success_url = reverse_lazy('admin_dashboard:user_list')
    
    def get_success_url(self):
        messages.success(self.request, "User deleted successfully.")
        return reverse('admin_dashboard:user_list')
