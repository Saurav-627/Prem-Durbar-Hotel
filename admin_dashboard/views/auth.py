from typing import cast
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse, reverse_lazy
from django.contrib import messages

class DashboardLoginView(LoginView):
    template_name = 'admin_dashboard/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self) -> str:
        return reverse('admin_dashboard:home')

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password. Please try again.")
        return super().form_invalid(form)

class DashboardLogoutView(LogoutView):
    next_page = cast(str, reverse_lazy('admin_dashboard:login'))

