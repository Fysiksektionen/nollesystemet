from django.urls import reverse_lazy
import django.contrib.auth.views as django_auth_views
from django.views.generic import TemplateView, UpdateView, ListView, CreateView

import authentication.views as auth_views
import fohseriet.utils as fohseriet_utils
import utils.misc as utils_misc
from utils.helper_views import MenuMixin

from .mixins import *
from .forms import *


class FohserietMenuMixin(MenuMixin):
    menu_item_info = fohseriet_utils.menu_item_info
    menu_items = ['index', 'hantera-event', 'hantera-andvandare', 'fadderiet', ['logga-in', 'logga-ut']]

class FohserietMenuView(FohserietMenuMixin, TemplateView):
    pass


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
