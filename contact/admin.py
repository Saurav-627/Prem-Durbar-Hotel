from django.contrib import admin

from .models.branch import Branch
from .models.category import ContactInquiryCategory
from .models.inquiry import ContactInquiry
from .models.newsletter import NewsletterSubscriber

@admin.register(ContactInquiryCategory)
class ContactInquiryCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'ordering', 'is_active')
    list_editable = ('ordering', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('email',)

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone', 'email', 'is_main', 'is_published')
    list_filter = ('is_main', 'is_published')
    list_editable = ('is_main', 'is_published')
    search_fields = ('name', 'address')

@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'category', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
