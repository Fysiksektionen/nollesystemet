"""
admin.py

Define ModelAdmins for custom edit behaviour in admin app and register to app.
This is for smooth development and backdoors for admins, not for user-side behavior.
"""

from django.contrib import admin, auth

from .models import AuthUser

class AuthUserAdmin(admin.ModelAdmin):
    model = AuthUser
    list_display = ['username', 'email']
    fields = ('username', 'last_login', 'email', 'groups', 'is_superuser', 'is_staff', 'is_active')
    readonly_fields = ('last_login', )


admin.site.register(AuthUser, AuthUserAdmin)
