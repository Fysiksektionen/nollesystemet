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

class SiteTextAdmin(admin.TabularInline):
    model = models.SiteText
    extra = 0
    readonly_fields = ('key',)
    fields = ('key', 'text')

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

class SiteImageAdmin(admin.TabularInline):
    model = models.SiteImage
    extra = 0
    readonly_fields = ('key',)
    fields = ('key', 'image')

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

class SiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'number_of_texts', 'number_of_images')
    inlines = [SiteTextAdmin, SiteImageAdmin]

    readonly_fields = ('name',)

    def number_of_texts(self, obj):
        return obj.texts.all().count()

    def number_of_images(self, obj):
        return obj.images.all().count()

    def has_add_permission(self, obj):
        return False

    def get_inlines(self, request, obj):
        inlines = []
        if self.number_of_texts(obj):
            inlines.append(SiteTextAdmin)
        if self.number_of_images(obj):
            inlines.append(SiteImageAdmin)
        return inlines


admin.site.register(models.Site, SiteAdmin)
