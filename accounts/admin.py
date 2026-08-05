from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models.user import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Custom Profile Info', {'fields': ('phone', 'is_hotel_admin', 'is_guest', 'avatar')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Custom Profile Info', {'fields': ('phone', 'is_hotel_admin', 'is_guest', 'avatar')}),
    )

