from django.contrib import admin, auth
from .models import UserProfile, UserGroup, AuthUser

admin.site.unregister(auth.models.Group)

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name = "User profile"
    verbose_name_plural = 'User profiles'

@admin.register(AuthUser)
class UserAdmin(admin.ModelAdmin):
    inlines = (UserProfileInline,)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    pass

@admin.register(UserGroup)
class UserGroupAdmin(admin.ModelAdmin):
    pass
