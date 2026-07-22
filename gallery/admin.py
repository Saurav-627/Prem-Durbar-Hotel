from django.contrib import admin
from .models.category import GalleryCategory
from .models.item import GalleryItem

@admin.register(GalleryCategory)
class GalleryCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_published')
    list_filter = ('is_published',)
    list_editable = ('is_published',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(GalleryItem)
class GalleryItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'category', 'caption', 'is_video', 'is_drone', 'is_published')
    list_filter = ('category', 'is_video', 'is_drone', 'is_published')
    list_editable = ('is_published',)
    search_fields = ('caption',)
