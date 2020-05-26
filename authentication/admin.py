"""
admin.py

Define ModelAdmins for custom edit behaviour in admin app and register to app.
This is for smooth development and backdoors for admins, not for user-side behavior.
"""

from django.contrib import admin, auth
from django.conf import settings
from .models import UserGroup, AuthUser
from django.apps import apps

admin.site.unregister(auth.models.Group)

class UserProfileInline(admin.StackedInline):
    model = apps.get_model(settings.USER_PROFILE_MODEL)
    can_delete = False
    verbose_name = "User profile"
    verbose_name_plural = 'User profiles'

@admin.register(AuthUser)
class UserAdmin(admin.ModelAdmin):
    inlines = (UserProfileInline,)

@admin.register(UserGroup)
class UserGroupAdmin(admin.ModelAdmin):
    pass
