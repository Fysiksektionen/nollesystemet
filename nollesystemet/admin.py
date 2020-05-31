from django.contrib import admin
import nollesystemet.models as models


@admin.register(models.DrinkOption)
class DrinkOptionAdmin(admin.ModelAdmin):
    pass

class DrinkOptionInline(admin.TabularInline):
    model = models.DrinkOption
    extra = 1


@admin.register(models.ExtraOption)
class ExtraOptionAdmin(admin.ModelAdmin):
    pass

class ExtraOptionInline(admin.TabularInline):
    model = models.ExtraOption
    extra = 1


@admin.register(models.GroupBasePrice)
class GroupHappeningPropertiesAdmin(admin.ModelAdmin):
    pass

class GroupHappeningPropertiesInline(admin.TabularInline):
    model = models.GroupBasePrice
    extra = 1


@admin.register(models.Happening)
class HappeningAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_time']
    inlines = [GroupHappeningPropertiesInline, DrinkOptionInline, ExtraOptionInline]

@admin.register(models.UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Registration)
class RegistrationAdmin(admin.ModelAdmin):
    pass