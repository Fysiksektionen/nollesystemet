"""
admin.py

Define ModelAdmins for custom edit behaviour in admin app and register to app.
This is for smooth development and backdoors for admins, not for user-side behavior.
"""

from django.contrib import admin, auth

from .models import AuthUser

admin.site.register(AuthUser)

