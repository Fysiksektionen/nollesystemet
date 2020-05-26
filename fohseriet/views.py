import django.contrib.auth.views as django_auth_views

import authentication.views as auth_views
from .forms import *
from .mixins import *


class MenuView(MenuMixin, TemplateView):
    menu_item_info = fohseriet_utils.menu_item_info
    menu_items = ['index', 'hantera-event', 'hantera-andvandare', 'fadderiet', ['logga-in', 'logga-ut']]


class LoginView(MenuView, auth_views.Login):
    default_redirect_url = reverse_lazy('fohseriet:index')
    template_name = 'fohseriet/logga-in/index.html'
    cred_login_url = reverse_lazy('fohseriet:logga-in:cred')
    cas_login_url = reverse_lazy('fohseriet:logga-in:cas')


class LogoutView(MenuView, django_auth_views.LogoutView):
    template_name = 'fohseriet/utloggad.html'


class LoginCredentialsView(MenuView, auth_views.LoginCred):
    template_name = 'fohseriet/logga-in/cred.html'
    default_redirect_url = reverse_lazy('fohseriet:index')

    form_class = utils_misc.make_crispy_form(auth_views.LoginCred.form_class, 'Logga in')


#This one needs to be updated to look more like the CreateView.
class HappeningUpdateView(UpdateView, HappeningOptionsMixin):
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


class HappeningCreateView(CreateView, HappeningOptionsMixin):
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


class HappeningListView(ListView):
    model = Happening
    template_name = 'fohseriet/evenemang/happening_list.html'
