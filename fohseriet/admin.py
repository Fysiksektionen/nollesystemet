from django.contrib import admin
from auth_app.models import AuthUser
from .models import UserProfile

admin.register(UserProfile)

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name = "User profile"
    verbose_name_plural = 'User profiles'

@admin.register(AuthUser)
class UserAdmin(admin.ModelAdmin):
    inlines = (UserProfileInline,)