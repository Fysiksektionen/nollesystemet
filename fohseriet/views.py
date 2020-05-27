import app as app
from django.apps import apps
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
import django.contrib.auth.views as django_auth_views
from django.views.generic import TemplateView, UpdateView, ListView, CreateView

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

#This one needs to be updated to look more like the CreateView.
class HappeningUpdateView(UpdateView, HappeningOptionsMixin, FohserietMenuMixin):
    model = Happening
    fields = '__all__'
    template_name = 'fohseriet/evenemang/create_happening.html'
    success_url = reverse_lazy('fohseriet:evenemang:lista')

    def get_context_data(self, **kwargs):
        context = super(HappeningUpdateView, self).get_context_data(**kwargs)
        if self.request.POST:
            context['drink_option_formset'] = DrinkOptionFormset(self.request.POST)
            context['base_price_formset'] = GroupHappeningPropertiesFormset(self.request.POST)
            context['extra_option_formset'] = ExtraOptionFormset(self.request.POST)
        else:
            context['drink_option_formset'] = DrinkOptionFormset()
            context['base_price_formset'] = GroupHappeningPropertiesFormset()
            context['extra_option_formset'] = ExtraOptionFormset()
        return context


class HappeningCreateView(CreateView, HappeningOptionsMixin, FohserietMenuMixin):
    model = Happening
    success_url = reverse_lazy('fohseriet:evenemang:lista')
    fields = '__all__'
    template_name = 'fohseriet/evenemang/create_happening.html'

    def get_context_data(self, **kwargs):
        context = super(HappeningCreateView, self).get_context_data(**kwargs)
        if self.request.POST:
            context['drink_option_formset'] = DrinkOptionFormset(self.request.POST)
            context['base_price_formset'] = GroupHappeningPropertiesFormset(self.request.POST)
            context['extra_option_formset'] = ExtraOptionFormset(self.request.POST)
        else:
            context['drink_option_formset'] = DrinkOptionFormset()
            context['base_price_formset'] = GroupHappeningPropertiesFormset()
            context['extra_option_formset'] = ExtraOptionFormset()
        return context


class HappeningListView(ListView, FohserietMenuMixin):
    model = Happening
    template_name = 'fohseriet/evenemang/happening_list.html'


# -------------------------------------------------------------------------------- #
# ----------------------------- User handeling views ----------------------------- #
# -------------------------------------------------------------------------------- #

class UsersListView(ListView, FohserietMenuMixin):
    model = apps.get_model(settings.AUTH_USER_MODEL)
    template_name = 'fohseriet/anvandare/index.html'

    extra_context = {
        'user_groups': apps.get_model('authentication.UserGroup').objects.filter(is_external=False),
        'nolle_groups': apps.get_model('authentication.NolleGroup').objects.all()
    }


class UserUpdateView(LoginRequiredMixin, FohserietMenuMixin, helper_views.MultipleObjectsUpdateView):
    model_list = [apps.get_model(settings.USER_PROFILE_MODEL), apps.get_model(settings.AUTH_USER_MODEL)]
    form_class_list = [ProfileUpdateForm, AuthUserGroupsUpdateForm]

    template_name = 'fohseriet/anvandare/uppdatera.html'
    success_url = reverse_lazy('fohseriet:anvandare:index')

    permission_denied_message = "Du har inte rättigheter till denna sida."

    def get_objects(self):
        auth_user = apps.get_model(settings.AUTH_USER_MODEL).objects.get(pk=self.kwargs['pk'])
        return auth_user.profile, auth_user

    def get_success_url(self):
        if REDIRECT_FIELD_NAME in self.request.GET:
            return self.request.GET[REDIRECT_FIELD_NAME]
        else:
            return super().get_success_url()