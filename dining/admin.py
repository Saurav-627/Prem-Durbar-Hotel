from django.contrib import admin
from .models.item import DiningCategory, DiningItem, DiningItemBasePrice

class DiningItemBasePriceInline(admin.TabularInline):
    model = DiningItemBasePrice
    extra = 1

@admin.register(DiningCategory)
class DiningCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'is_published')
    list_editable = ('order', 'is_published')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(DiningItem)
class DiningItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'base_price', 'is_vegetarian', 'is_spicy', 'is_chef_special', 'is_published')
    list_filter = ('category', 'is_vegetarian', 'is_spicy', 'is_chef_special', 'is_published')
    list_editable = ('base_price', 'is_vegetarian', 'is_spicy', 'is_chef_special', 'is_published')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [DiningItemBasePriceInline]
