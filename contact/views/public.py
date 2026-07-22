from django.views.generic import TemplateView
from ..models.branch import Branch

class ContactView(TemplateView):
    template_name = 'contact/contact.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['branches'] = Branch.objects.filter(is_published=True).order_by('-is_main')
        return context
