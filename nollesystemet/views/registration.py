from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView

import nollesystemet.models as models
import nollesystemet.forms as forms
import nollesystemet.mixins as mixins


class RegistrationView(LoginRequiredMixin, UserPassesTestMixin, mixins.FadderietMenuMixin, UpdateView):
    model = models.Registration
    form_class = forms.RegistrationForm
    template_name = 'fadderiet/evenemang/anmalan.html'

    success_url = reverse_lazy('fadderiet:evenemang:index')

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        try:
            self.happening = models.Happening.objects.get(pk=self.kwargs['pk'])
        except models.Happening.DoesNotExist:
            self.happening = None
        else:
            try:
                self.registration = models.Registration.objects.get(user=self.request.user.profile, happening=self.happening)
            except:
                if self.happening is None:
                    self.raise_exception = True
                    self.handle_no_permission()
                else:
                    self.registration = None
        self.registration_user = self.request.user.profile
        self.observing_user = self.request.user.profile

    def test_func(self):
        if self.registration:
            return self.registration.user_can_edit_registration(self.observing_user)
        else:
            return self.happening.user_can_register(self.observing_user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'happening': self.happening,
            'observing_user': self.observing_user,
            'user': self.request.user.profile,
        })
        return kwargs

    def get_initial(self):
        if self.request.user.profile.food_preference:
            self.initial.update({'food_preference': self.request.user.profile.food_preference})
        return super().get_initial()

    def get_object(self, queryset=None):
        return self.registration

    def get_context_data(self, **kwargs):
        dynamic_extra_context = {
            'happening': self.happening
        }
        kwargs.update(**dynamic_extra_context)
        return super().get_context_data(**kwargs)

class RegistrationUpdateView(LoginRequiredMixin, UserPassesTestMixin, mixins.FohserietMenuMixin, mixins.RedirectToGETArgMixin, UpdateView):
    model = models.Registration
    form_class = forms.RegistrationForm
    template_name = 'fohseriet/anmalan/redigera.html'

    success_url = reverse_lazy('fohseriet:index')

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        try:
            self.registration = models.Registration.objects.get(pk=self.kwargs['pk'])
        except models.Registration.DoesNotExist:
            self.raise_exception = True
            self.handle_no_permission()

        self.happening = self.registration.happening
        self.registration_user = self.registration.user
        self.observing_user = self.request.user.profile

    def test_func(self):
        return self.registration.user_can_see_registration(self.request.user.profile)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'observing_user': self.observing_user
        })
        return kwargs
