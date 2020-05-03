from django.contrib import admin
from .models import *

@admin.register(DrinkOption)
class DrinkOptionAdmin(admin.ModelAdmin):
    pass

class DrinkOptionInline(admin.TabularInline):
    model = DrinkOption
    extra = 1


@admin.register(ExtraOption)
class ExtraOptionAdmin(admin.ModelAdmin):
    pass

class ExtraOptionInline(admin.TabularInline):
    model = ExtraOption
    extra = 1


@admin.register(GroupHappeningProperties)
class GroupHappeningPropertiesAdmin(admin.ModelAdmin):
    pass

class GroupHappeningPropertiesInline(admin.TabularInline):
    model = GroupHappeningProperties
    extra = 1


@admin.register(Happening)
class HappeningAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_time']
    inlines = [GroupHappeningPropertiesInline, DrinkOptionInline, ExtraOptionInline]

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    pass

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    pass

