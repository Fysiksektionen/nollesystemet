from django.apps import apps
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy
from django.contrib import admin
from django.contrib.auth import models as django_auth_models
from django.conf import settings

import logging

import nollesystemet.models as models
from nollesystemet.forms import PasswordResetForm


class SuperAdminSite(admin.AdminSite):
    site_url = '/fohseriet/'
    site_title = gettext_lazy('nØllesystemet admin')
    site_header = gettext_lazy('Superadminsida')
    index_title = gettext_lazy('Superadmin')

    def has_permission(self, request):
        return request.user.is_active and request.user.is_staff and request.user.is_superuser


class MottagningensAdminSite(admin.AdminSite):
    site_url = '/fohseriet/'
    site_title = gettext_lazy('nØllesystemet admin')
    site_header = gettext_lazy('Mottagningens adminsida')
    index_title = gettext_lazy('Mottagningen')

    def has_permission(self, request):
        return request.user.is_active and request.user.profile.has_perm('nollesystemet.edit_system')


logger = logging.getLogger('reset_mail_logger')
def send_reset_password(modeladmin, request, queryset):
    for user in queryset:
        if user.auth_user.has_usable_password():
            try:
                reset_form = PasswordResetForm(data={'email': user.auth_user.email})
                reset_form.is_valid()
                reset_form.save(
                    request=request,
                    use_https=request.is_secure(),
                    email_template_name='fadderiet/aterstall-losenord/epost.txt',
                    html_email_template_name='fadderiet/aterstall-losenord/epost.html',
                    subject_template_name='fadderiet/aterstall-losenord/epost-amne.txt'
                )
            except Exception as e:
                logger.error("User %s got no mail" % str(user))
send_reset_password.short_description = "Skicka återställning av lösenord"


class SingeltonAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class UserProfileAdmin(admin.ModelAdmin):
    ordering = ['first_name', 'last_name']
    list_display = ('__str__', 'email', 'type', 'nolle_group', 'have_filled_nolleForm')
    list_filter = ('user_type', 'nolle_group')
    list_per_page = 500
    list_max_show_all = 500
    actions = [send_reset_password]

    def have_filled_nolleForm(self, instance):
        if instance.nolleformanswer is not None:
            return True
        else:
            if instance.is_nollan():
                return False
            else:
                return None


class DrinkOptionInline(admin.TabularInline):
    model = models.DrinkOption
    extra = 1


class ExtraOptionInline(admin.TabularInline):
    model = models.ExtraOption
    extra = 1


class UserTypeBasePriceInline(admin.TabularInline):
    model = models.UserTypeBasePrice
    extra = 1

class RegistrationInline(admin.TabularInline):
    readonly_fields = ("user", "confirmed")
    model = models.Registration
    extra = 0

class HappeningAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_time']
    inlines = [RegistrationInline, UserTypeBasePriceInline, DrinkOptionInline, ExtraOptionInline]

class NolleGroupsRestrictedAdmin(admin.ModelAdmin):
    ordering = ('name',)
    exclude = ('schedule',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return super(NolleGroupsRestrictedAdmin, self).has_change_permission(request, obj=obj) or \
               request.user.profile.has_perm('nollesystemet.edit_system')


class SiteTextAdmin(admin.TabularInline):
    model = models.SiteText
    extra = 0
    readonly_fields = ('key',)
    fields = ('key', 'text')

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return super(SiteTextAdmin, self).has_change_permission(request, obj=obj) or \
               request.user.profile.has_perm('nollesystemet.edit_system')

class SiteImageAdmin(admin.TabularInline):
    model = models.SiteImage
    extra = 0
    readonly_fields = ('key',)
    fields = ('key', 'image')

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return super(SiteImageAdmin, self).has_change_permission(request, obj=obj) or \
               request.user.profile.has_perm('nollesystemet.edit_system')

class SiteParagraphAdmin(admin.StackedInline):
    model = models.SiteParagraph
    extra = 0
    fields = ('order_num', 'title', 'text', 'image')

    def has_add_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        return super(SiteParagraphAdmin, self).has_change_permission(request, obj=obj) or \
               request.user.profile.has_perm('nollesystemet.edit_system')

class SiteParagraphListAdmin(admin.ModelAdmin):
    fields = ('key', 'site')
    readonly_fields = ('key', 'site')
    inlines = [SiteParagraphAdmin]

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return super(SiteParagraphListAdmin, self).has_change_permission(request, obj=obj) or \
               request.user.profile.has_perm('nollesystemet.edit_system')

class SiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'number_of_texts', 'number_of_images', 'number_of_lists')
    inlines = [SiteTextAdmin, SiteImageAdmin]
    readonly_fields = ('name',)
    fields = ('name',)

    def number_of_texts(self, obj):
        return obj.texts.all().count()

    def number_of_images(self, obj):
        return obj.images.all().count()

    def number_of_lists(self, obj):
        return obj.paragraph_lists.all().count()

    def has_add_permission(self, obj):
        return False

    def get_inlines(self, request, obj):
        inlines = []
        if self.number_of_texts(obj):
            inlines.append(SiteTextAdmin)
        if self.number_of_images(obj):
            inlines.append(SiteImageAdmin)
        return inlines

    def has_change_permission(self, request, obj=None):
        return super(SiteAdmin, self).has_change_permission(request, obj=obj) or \
               request.user.profile.has_perm('nollesystemet.edit_system')

class SiteAdminMottagningen(SiteAdmin):
    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        return False

class AuthUserAdmin(admin.ModelAdmin):
    list_display = ('upper_case_name',)

    def upper_case_name(self, obj):
        return "%s" % str(obj.profile)
    upper_case_name.short_description = 'Name'


class RegistrationAdmin(admin.ModelAdmin):
    fields = ['happening', 'user', 'food_preference', 'drink_option', 'extra_option', 'other', 'created_at', 'updated_at', 'paid', 'attended']
    readonly_fields = ['happening', 'user', 'created_at', 'updated_at', 'paid', 'attended']

class DynamicNolleFormQuestionAnswerAdmin(admin.TabularInline):
    fields = ("pk", "value", "group")
    readonly_fields = ("pk", "value", "group")
    model = models.DynamicNolleFormQuestionAnswer
    extra = 0

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

class DynamicNolleFormQuestionAdmin(admin.ModelAdmin):
    inlines = [DynamicNolleFormQuestionAnswerAdmin]

class NolleFormAnswerAdmin(admin.ModelAdmin):
    inlines = [DynamicNolleFormQuestionAnswerAdmin]


superadmin_admin_site = SuperAdminSite(name='super-admin')
mottagningen_admin_site = MottagningensAdminSite(name='nolle-admin')

mottagningen_admin_site.register(models.NolleGroup, NolleGroupsRestrictedAdmin)
mottagningen_admin_site.register(models.SiteParagraphList, SiteParagraphListAdmin)
mottagningen_admin_site.register(models.Site, SiteAdminMottagningen)
mottagningen_admin_site.register(models.HappeningSettings, SingeltonAdmin)
mottagningen_admin_site.register(models.SiteSettings, SingeltonAdmin)

superadmin_admin_site.register(models.Happening, HappeningAdmin)
superadmin_admin_site.register(models.HappeningSettings, SingeltonAdmin)
superadmin_admin_site.register(models.UserProfile, UserProfileAdmin)
superadmin_admin_site.register(models.NolleGroup, NolleGroupsRestrictedAdmin)
superadmin_admin_site.register(models.Registration, RegistrationAdmin)
superadmin_admin_site.register(models.Site, SiteAdmin)
superadmin_admin_site.register(models.SiteSettings, SingeltonAdmin)
superadmin_admin_site.register(models.SiteParagraphList, SiteParagraphListAdmin)
superadmin_admin_site.register(models.UserTypeBasePrice)
superadmin_admin_site.register(models.ExtraOption)
superadmin_admin_site.register(models.DrinkOption)
superadmin_admin_site.register(models.NolleFormAnswer)
superadmin_admin_site.register(models.DynamicNolleFormQuestion, DynamicNolleFormQuestionAdmin)
superadmin_admin_site.register(django_auth_models.Group)
superadmin_admin_site.register(apps.get_model(settings.AUTH_USER_MODEL), AuthUserAdmin)


