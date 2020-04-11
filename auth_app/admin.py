from django.contrib import admin
from django.contrib.auth.models import Group
from .models import AuthUser, AuthUserGroup, UserProfile
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name = "User profile"
    verbose_name_plural = 'User profiles'

@admin.register(AuthUser)
class UserAdmin(admin.ModelAdmin):
    inlines = (UserProfileInline,)


admin.site.unregister(Group)
admin.site.register(AuthUserGroup)
