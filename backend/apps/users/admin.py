"""
Django admin configuration for users app
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, NotificationPreferences


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User admin"""

    list_display = ('email', 'username', 'oauth_provider', 'is_premium', 'is_active', 'created_at')
    list_filter = ('oauth_provider', 'is_premium', 'is_active', 'is_staff', 'created_at')
    search_fields = ('email', 'username', 'oauth_id')
    ordering = ('-created_at',)

    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('OAuth', {'fields': ('oauth_provider', 'oauth_id', 'profile_image')}),
        ('Preferences', {'fields': ('timezone',)}),
        ('Premium', {'fields': ('is_premium', 'premium_expires_at')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

    readonly_fields = ('created_at', 'updated_at')

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )


@admin.register(NotificationPreferences)
class NotificationPreferencesAdmin(admin.ModelAdmin):
    """NotificationPreferences admin"""

    list_display = ('user', 'sound_enabled', 'screen_flash_enabled', 'vibration_enabled', 'device_flash_enabled')
    list_filter = ('sound_enabled', 'screen_flash_enabled', 'vibration_enabled', 'device_flash_enabled')
    search_fields = ('user__email', 'user__username')

    fieldsets = (
        (None, {'fields': ('user',)}),
        ('Notification Settings', {
            'fields': ('sound_enabled', 'screen_flash_enabled', 'vibration_enabled', 'device_flash_enabled')
        }),
        ('Flash Pattern', {'fields': ('flash_pattern',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

    readonly_fields = ('created_at', 'updated_at')
