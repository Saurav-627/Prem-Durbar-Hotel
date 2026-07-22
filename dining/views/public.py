from django.views.generic import ListView, DetailView
from ..models.venue import DiningVenue

class DiningListView(ListView):
    model = DiningVenue
    template_name = 'dining/dining_list.html'
    context_object_name = 'venues'

    def get_queryset(self):
        return DiningVenue.objects.filter(is_published=True)

class DiningDetailView(DetailView):
    model = DiningVenue
    template_name = 'dining/dining_detail.html'
    context_object_name = 'venue'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return DiningVenue.objects.filter(is_published=True)
