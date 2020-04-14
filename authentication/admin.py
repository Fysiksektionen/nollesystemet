"""
admin.py

Define ModelAdmins for custom edit behaviour in admin app and register to app.
This is for smooth development and backdoors for admins, not for user-side behavior.
"""

from django.apps import apps
from django.contrib import admin, auth

import authentication.utils as utils
from .models import UserGroup, AuthUser, NolleGroup

# Don't keep the default Group model.
admin.site.unregister(auth.models.Group)

class UserProfileInline(admin.StackedInline):
    """ Defines behaviour of inline edit of USER_PROFILE_MODEL """

    model = apps.get_model(utils.get_setting('USER_PROFILE_MODEL'))
    can_delete = False
    verbose_name = "User profile"
    verbose_name_plural = 'User profiles'

@admin.register(AuthUser)
class UserAdmin(admin.ModelAdmin):
    inlines = (UserProfileInline,)


@admin.register(UserGroup)
class UserGroupAdmin(admin.ModelAdmin):
    pass

@admin.register(NolleGroup)
class NolleGroupAdmin(admin.ModelAdmin):
    pass
