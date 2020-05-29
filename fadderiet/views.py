import django.contrib.auth.views as django_auth_views
from django.apps import apps
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, UpdateView

import authentication.views as auth_views
import fadderiet.forms as forms
import fadderiet.utils as fadderiet_utils
import utils.misc as utils_misc
import utils.helper_views as helper_views
from fohseriet.models import Happening, Registration


class FadderietMenuMixin(helper_views.MenuMixin):
    menu_item_info = fadderiet_utils.menu_item_info
    menu_items = ['index', 'schema', 'bra-info', 'om-fadderiet', 'evenemang', 'kontakt', 'mina-sidor:profil', ['logga-in', 'logga-ut']]

class FadderietMenuView(FadderietMenuMixin, TemplateView):
    pass

class LoginView(FadderietMenuMixin, auth_views.login.Login):
    default_redirect_url = reverse_lazy('fadderiet:index')
    template_name = 'fadderiet/logga-in/index.html'
    cred_login_url = reverse_lazy('fadderiet:logga-in:nollan')
    cas_login_url = reverse_lazy('fadderiet:logga-in:fadder')


class LogoutView(FadderietMenuMixin, django_auth_views.LogoutView):
    template_name = 'fadderiet/utloggad.html'


class LoginCredentialsView(FadderietMenuMixin, auth_views.login.LoginCred):
    template_name = 'fadderiet/logga-in/nollan.html'
    default_redirect_url = reverse_lazy('fadderiet:index')

    form_class = utils_misc.make_crispy_form(auth_views.login.LoginCred.form_class, 'Logga in')

    extra_context = {
        'reset_password_url': reverse_lazy('fadderiet:aterstall-losenord:index'),
        'register_url': reverse_lazy('fadderiet:registrera-dig')
    }


class RegisterView(FadderietMenuMixin, auth_views.user.AuthUserCreateView):
    template_name = 'fadderiet/registrera-dig.html'
    success_url = reverse_lazy('fadderiet:logga-in:index')

    form_class = fadderiet_utils.make_crispy_form(auth_views.user.AuthUserCreateView.form_class, 'Registrera')


class PasswordChangeView(FadderietMenuMixin, auth_views.password.PasswordChangeView):
    success_url = reverse_lazy('authentication:password_change_done')
    template_name = 'fadderiet/byt-losenord/index.html'
    form_class = fadderiet_utils.make_crispy_form(auth_views.password.PasswordChangeView.form_class, submit_button='Byt lösenord')

class PasswordChangeDoneView(FadderietMenuMixin, auth_views.password.PasswordChangeDoneView):
    template_name = 'fadderiet/byt-losenord/klart.html'

class PasswordResetView(FadderietMenuMixin, auth_views.password.PasswordResetView):
    email_template_name = 'fadderiet/aterstall-losenord-epost.html'
    subject_template_name = 'fadderiet/aterstall-losenord-epost-amne.txt'
    success_url = reverse_lazy('fadderiet:aterstall-losenord:skickat')
    template_name = 'fadderiet/aterstall-losenord/index.html'
    form_class = fadderiet_utils.make_crispy_form(auth_views.password.PasswordResetView.form_class, submit_button='Återställ lösenord')

class PasswordResetDoneView(FadderietMenuMixin, auth_views.password.PasswordResetDoneView):
    template_name = 'fadderiet/aterstall-losenord/skickat.html'

class PasswordResetConfirmView(FadderietMenuMixin, auth_views.password.PasswordResetConfirmView):
    template_name = 'fadderiet/aterstall-losenord/lank.html'
    success_url = reverse_lazy('fadderiet:aterstall-losenord:klart')
    form_class = fadderiet_utils.make_crispy_form(auth_views.password.PasswordResetConfirmView.form_class, submit_button='Sätt nytt lösenord')

class PasswordResetCompleteView(FadderietMenuMixin, auth_views.password.PasswordResetCompleteView):
    template_name = 'fadderiet/aterstall-losenord/klart.html'
    extra_context = {'login_url': reverse_lazy('fadderiet:logga-in:index')}


class ProfilePageView(LoginRequiredMixin, FadderietMenuMixin, helper_views.MultipleObjectsUpdateView):
    model_list = [apps.get_model(settings.AUTH_USER_MODEL), apps.get_model(settings.USER_PROFILE_MODEL)]
    form_class_list = [forms.AuthUserUpdateForm, forms.ProfileUpdateForm]

    template_name = 'fadderiet/mina-sidor/profil.html'
    success_url = reverse_lazy('fadderiet:mina-sidor:profil')

    extra_context = {
        'change_password_url': reverse_lazy('fadderiet:byt-losenord:index')
    }

    def get_objects(self):
        return self.request.user, self.request.user.profile

    def form_valid(self, forms):
        self.request.user.profile.has_set_profile = True
        return super().form_valid(forms)

    def get_success_url(self):
        if REDIRECT_FIELD_NAME in self.request.GET:
            return self.request.GET[REDIRECT_FIELD_NAME]
        else:
            return super().get_success_url()


class HappeningListView(LoginRequiredMixin, FadderietMenuMixin, ListView):
    model = Happening
    template_name = 'fadderiet/evenemang/index.html'

    ordering = 'start_time'

    def get_queryset(self):
        self.queryset = Happening.objects.filter(user_groups__in=self.request.user.user_group.all()).filter(nolle_groups=self.request.user.nolle_group)
        querryset = super().get_queryset()
        return [{'happening': happening, 'is_registered': Registration.objects.filter(user=self.request.user.profile).filter(happening=happening).count() > 0} for happening in querryset]


class RegistrationView(LoginRequiredMixin, UserPassesTestMixin, FadderietMenuMixin, UpdateView):
    model = Registration
    form_class = forms.RegistrationForm
    template_name = 'fadderiet/evenemang/anmalan.html'

    success_url = reverse_lazy('fadderiet:evenemang:index')

    def test_func(self):
        happening = Happening.objects.get(pk=self.kwargs['pk'])
        return happening in Happening.objects.filter(user_groups__in=self.request.user.user_group.all()).filter(nolle_groups=self.request.user.nolle_group)

    def get_form_class(self):
        return utils_misc.make_crispy_form(super().get_form_class(), submit_button='Skicka')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'happening': Happening.objects.get(pk=self.kwargs['pk']),
            'user': self.request.user.profile
        })
        return kwargs

    def get_initial(self):
        if self.request.user.profile.food_preference:
            self.initial.update({'food_preference': self.request.user.profile.food_preference})
        return super().get_initial()

    def get_form(self, form_class=None):
        form = super().get_form(form_class=None)
        if self.object is not None:
            for field_name in form.fields:
                form.fields[field_name].widget.attrs['disabled'] = True
            form.helper.inputs.pop()
        return form

    def get_object(self, queryset=None):
        happening = Happening.objects.get(pk=self.kwargs['pk'])
        try:
            return Registration.objects.get(user=self.request.user.profile, happening=happening)
        except Registration.DoesNotExist:
            return None

    def get_context_data(self, **kwargs):
        dynamic_extra_context = {
            'happening': Happening.objects.get(pk=self.kwargs['pk'])
        }
        kwargs.update(**dynamic_extra_context)
        return super().get_context_data(**kwargs)