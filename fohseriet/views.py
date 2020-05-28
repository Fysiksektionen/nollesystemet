import app as app
from django.apps import apps
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
import django.contrib.auth.views as django_auth_views
from django.views.generic import TemplateView, UpdateView, ListView, CreateView
from braces.views import MultiplePermissionsRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin

import authentication.views as auth_views
import fohseriet.utils as fohseriet_utils
import utils.helper_views as helper_views
import utils.misc as utils_misc
from fadderiet.forms import ProfileUpdateForm
from .mixins import *
from .forms import *


class FohserietMenuMixin(helper_views.MenuMixin):
    menu_item_info = fohseriet_utils.menu_item_info
    menu_items = ['index', 'hantera-event', 'hantera-andvandare', 'fadderiet', ['logga-in', 'logga-ut']]

class FohserietMenuView(FohserietMenuMixin, TemplateView):
    pass


# -------------------------------------------------------------------------------- #
# --------------------------------- Login views ---------------------------------- #
# -------------------------------------------------------------------------------- #


class LoginView(auth_views.Login, FohserietMenuMixin):
    default_redirect_url = reverse_lazy('fohseriet:index')
    template_name = 'fohseriet/logga-in/index.html'
    cred_login_url = reverse_lazy('fohseriet:logga-in:cred')
    cas_login_url = reverse_lazy('fohseriet:logga-in:cas')


class LogoutView(django_auth_views.LogoutView, FohserietMenuMixin):
    template_name = 'fohseriet/utloggad.html'


class LoginCredentialsView(auth_views.LoginCred, FohserietMenuMixin):
    template_name = 'fohseriet/logga-in/cred.html'
    default_redirect_url = reverse_lazy('fohseriet:index')

    form_class = utils_misc.make_crispy_form(auth_views.LoginCred.form_class, 'Logga in')


# -------------------------------------------------------------------------------- #
# ------------------------------- Happening views -------------------------------- #
# -------------------------------------------------------------------------------- #

class HappeningListView(LoginRequiredMixin, PermissionRequiredMixin, FohserietMenuMixin, ListView):
    model = Happening
    template_name = 'fohseriet/evenemang/index.html'

    ordering = 'start_time'

    permission_required = 'fohseriet.edit_happening'

    def get_queryset(self):
        self.queryset = Happening.objects.all()
        querryset = super().get_queryset()
        return [{'happening': happening,
                 'user_can_edit': self.request.user.profile in happening.editors.all()} for happening in querryset]


class HappeningRegisteredListView(LoginRequiredMixin, UserPassesTestMixin, FohserietMenuMixin, ListView):
    model = Registration
    template_name = 'fohseriet/evenemang/anmalda.html'

    ordering = 'user__first_name'

    extra_context = {
        'user_groups': apps.get_model('authentication.UserGroup').objects.filter(is_external=False),
        'nolle_groups': apps.get_model('authentication.NolleGroup').objects.all()
    }

    def test_func(self):
        return self.request.user.has_perm(
            'fohseriet.edit_happening') and self.request.user.profile in Happening.objects.get(
            pk=self.kwargs['pk']).editors.all()

    def get_queryset(self):
        self.queryset = Registration.objects.filter(happening=Happening.objects.get(pk=self.kwargs['pk']))
        querryset = super().get_queryset()
        return querryset
        # return [{'happening': happening,
        #          'user_can_edit': self.request.user.profile in happening.editors.all()} for happening in querryset]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'happening': Happening.objects.get(pk=self.kwargs['pk'])
        })
        return context

class HappeningUpdateView(LoginRequiredMixin, UserPassesTestMixin, HappeningOptionsMixin, FohserietMenuMixin, UpdateView):
    model = Happening
    form_class = HappeningForm

    success_url = reverse_lazy('fohseriet:evenemang:lista')
    template_name = 'fohseriet/evenemang/redigera.html'

    def test_func(self):
        return self.request.user.has_perm('fohseriet.edit_happening') and self.request.user.profile in Happening.objects.get(pk=self.kwargs['pk']).editors.all() if 'pk' in self.kwargs else True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        formset_kwargs = {}

        if self.request.POST:
            formset_kwargs['data'] = self.request.POST
        if self.object:
            formset_kwargs['instance'] = self.object

        context['drink_option_formset'] = DrinkOptionFormset(**formset_kwargs)
        context['base_price_formset'] = GroupBasePriceFormset(**formset_kwargs)
        context['extra_option_formset'] = ExtraOptionFormset(**formset_kwargs)

        return context

    def get_object(self, queryset=None):
        if 'pk' not in self.kwargs:
            return None
        return super().get_object(queryset=queryset)


# -------------------------------------------------------------------------------- #
# ----------------------------- User handeling views ----------------------------- #
# -------------------------------------------------------------------------------- #

class UsersListView(LoginRequiredMixin, MultiplePermissionsRequiredMixin, FohserietMenuMixin, ListView):
    model = apps.get_model(settings.AUTH_USER_MODEL)
    template_name = 'fohseriet/anvandare/index.html'

    permissions = {
        "any": ("fohseriet.edit_user_info", "fohseriet.edit_user_registrations")
    }

    extra_context = {
        'user_groups': apps.get_model('authentication.UserGroup').objects.filter(is_external=False),
        'nolle_groups': apps.get_model('authentication.NolleGroup').objects.all()
    }


class UserUpdateView(LoginRequiredMixin, PermissionRequiredMixin, FohserietMenuMixin, helper_views.MultipleObjectsUpdateView):
    model_list = [apps.get_model(settings.USER_PROFILE_MODEL), apps.get_model(settings.AUTH_USER_MODEL)]
    form_class_list = [ProfileUpdateForm, AuthUserGroupsUpdateForm]

    template_name = 'fohseriet/anvandare/uppdatera.html'
    success_url = reverse_lazy('fohseriet:anvandare:index')

    permission_required = 'fohseriet.edit_user_info'

    def get_objects(self):
        auth_user = apps.get_model(settings.AUTH_USER_MODEL).objects.get(pk=self.kwargs['pk'])
        return auth_user.profile, auth_user

    def get_success_url(self):
        if REDIRECT_FIELD_NAME in self.request.GET:
            return self.request.GET[REDIRECT_FIELD_NAME]
        else:
            return super().get_success_url()