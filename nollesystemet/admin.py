from django.contrib import admin
import nollesystemet.models as models


admin.site.register(models.UserProfile)
admin.site.register(models.NolleGroup)
admin.site.register(models.Registration)


class DrinkOptionInline(admin.TabularInline):
    model = models.DrinkOption
    extra = 1


class ExtraOptionInline(admin.TabularInline):
    model = models.ExtraOption
    extra = 1


class UserTypeBasePriceInline(admin.TabularInline):
    model = models.UserTypeBasePrice
    extra = 1


admin.site.register(models.Happening)
class HappeningAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_time']
    inlines = [UserTypeBasePriceInline, DrinkOptionInline, ExtraOptionInline]


admin.site.register(models.UserTypeBasePrice)
admin.site.register(models.ExtraOption)
admin.site.register(models.DrinkOption)


