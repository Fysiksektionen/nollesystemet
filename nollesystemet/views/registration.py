from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView

import utils.misc as utils_misc
import utils.helper_views as helper_views

import nollesystemet.models as models
import nollesystemet.forms as forms
import nollesystemet.mixins as mixins


class RegistrationView(LoginRequiredMixin, UserPassesTestMixin, mixins.FadderietMenuMixin, UpdateView):
    model = models.registration.Registration
    form_class = forms.RegistrationForm
    template_name = 'fadderiet/evenemang/anmalan.html'

    success_url = reverse_lazy('fadderiet:evenemang:index')

    def test_func(self):
        happening = models.happening.Happening.objects.get(pk=self.kwargs['pk'])
        return happening in models.happening.Happening.objects.filter(user_groups__in=self.request.user.user_group.all()).filter(nolle_groups=self.request.user.nolle_group)

    def get_form_class(self):
        return utils_misc.make_crispy_form(super().get_form_class(), submit_button='Skicka')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'happening': models.happening.Happening.objects.get(pk=self.kwargs['pk']),
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
        happening = models.happening.Happening.objects.get(pk=self.kwargs['pk'])
        try:
            return models.registration.Registration.objects.get(user=self.request.user.profile, happening=happening)
        except models.registration.Registration.DoesNotExist:
            return None

    def get_context_data(self, **kwargs):
        dynamic_extra_context = {
            'happening': models.happening.Happening.objects.get(pk=self.kwargs['pk'])
        }
        kwargs.update(**dynamic_extra_context)
        return super().get_context_data(**kwargs)

class RegistrationUpdateView(LoginRequiredMixin, UserPassesTestMixin, mixins.FohserietMenuMixin, helper_views.RedirectToGETArgMixin, UpdateView):
    model = models.registration.Registration
    form_class = forms.RegistrationForm
    template_name = 'fohseriet/anmalan/redigera.html'

    success_url = reverse_lazy('fohseriet:index')

    def test_func(self):
        return self.request.user.has_perm(
            'fohseriet.edit_user_registration') or self.request.user.profile in models.registration.Registration.objects.get(
            pk=self.kwargs['pk']).happening.editors.all()

    def get_form_class(self):
        return utils_misc.make_crispy_form(super().get_form_class(), submit_button='Spara')

    def get_object(self, queryset=None):
        try:
            return models.registration.Registration.objects.get(pk=self.kwargs['pk'])
        except models.registration.Registration.DoesNotExist:
            return None
