from django.contrib import admin
import nollesystemet.models as models


@admin.register(models.happening.DrinkOption)
class DrinkOptionAdmin(admin.ModelAdmin):
    pass

class DrinkOptionInline(admin.TabularInline):
    model = models.happening.DrinkOption
    extra = 1


@admin.register(models.happening.ExtraOption)
class ExtraOptionAdmin(admin.ModelAdmin):
    pass

class ExtraOptionInline(admin.TabularInline):
    model = models.happening.ExtraOption
    extra = 1


@admin.register(models.happening.GroupBasePrice)
class GroupHappeningPropertiesAdmin(admin.ModelAdmin):
    pass

class GroupHappeningPropertiesInline(admin.TabularInline):
    model = models.happening.GroupBasePrice
    extra = 1


@admin.register(models.happening.Happening)
class HappeningAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_time']
    inlines = [GroupHappeningPropertiesInline, DrinkOptionInline, ExtraOptionInline]

@admin.register(models.user.UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    pass

@admin.register(models.registration.Registration)
class RegistrationAdmin(admin.ModelAdmin):
    pass