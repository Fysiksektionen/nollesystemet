"""
admin.py

Define ModelAdmins for custom edit behaviour in admin app and register to app.
This is for smooth development and backdoors for admins, not for user-side behavior.
"""

from django.contrib import admin, auth

from .models import UserGroup, AuthUser, NolleGroup

# Don't keep the default Group model.
admin.site.unregister(auth.models.Group)

@admin.register(AuthUser)
class UserAdmin(admin.ModelAdmin):
    pass

@admin.register(UserGroup)
class UserGroupAdmin(admin.ModelAdmin):
    pass

@admin.register(NolleGroup)
class NolleGroupAdmin(admin.ModelAdmin):
    pass
