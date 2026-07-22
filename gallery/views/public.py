from django.views.generic import ListView
from ..models.category import GalleryCategory
from ..models.item import GalleryItem

class GalleryListView(ListView):
    model = GalleryItem
    template_name = 'gallery/gallery_list.html'
    context_object_name = 'items'

    def get_queryset(self):
        return GalleryItem.objects.filter(is_published=True, category__is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = GalleryCategory.objects.filter(is_published=True)
        return context
