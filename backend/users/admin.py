from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User

class UserAdmin(BaseUserAdmin):
    list_display = ('phone_number', 'email', 'first_name', 'last_name', 'user_role', 'is_active', 'is_staff')
    list_filter = ('user_role', 'is_active', 'is_staff')
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Profile'), {'fields': ('user_role', 'profile_photo_url', 'preferred_language')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'email', 'first_name', 'last_name', 'user_role', 'password1', 'password2'),
        }),
    )
    search_fields = ('phone_number', 'email', 'first_name', 'last_name')
    ordering = ('phone_number',)

admin.site.register(User, UserAdmin)