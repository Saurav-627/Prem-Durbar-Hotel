from django.contrib import admin
from .models.branch import Branch
from .models.inquiry import ContactInquiry

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
