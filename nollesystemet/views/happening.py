import collections
import csv
from typing import Callable, Any

from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse_lazy, reverse
from django.utils.text import slugify
from django.views import View
from django.views.generic import UpdateView, ListView
from django.views.generic.edit import FormMixin, ProcessFormView

import nollesystemet.models as models
import nollesystemet.forms as forms
import nollesystemet.mixins as mixins
from nollesystemet.views.misc import DownloadView


class HappeningListViewFadderiet(mixins.FadderietMixin, ListView):
    model = models.Happening
    template_name = 'fadderiet/evenemang/index.html'

    ordering = 'start_time'

    login_required = True

    def get_queryset(self):
        self.queryset = models.Happening.objects.filter(user_groups__in=self.request.user.user_group.all()).filter(nolle_groups=self.request.user.nolle_group)
        querryset = super().get_queryset()
        return [{'happening': happening, 'is_registered': models.Registration.objects.filter(user=self.request.user.profile).filter(happening=happening).count() > 0} for happening in querryset]

class HappeningListViewFohseriet(mixins.FohserietMixin, ListView):
    model = models.Happening
    template_name = 'fohseriet/evenemang/index.html'

    ordering = 'start_time'

    login_required = True
    permission_required = 'nollesystemet.edit_happening'

    def get_queryset(self):
        self.queryset = models.Happening.objects.all()
        querryset = super().get_queryset()
        return [{'happening': happening,
                 'user_can_edit': self.request.user.profile in happening.editors.all()} for happening in querryset]


class HappeningRegisteredListView(mixins.FohserietMixin, ListView):
    model = models.Registration
    template_name = 'fohseriet/evenemang/anmalda.html'

    default_back_url = reverse_lazy('fohseriet:evenemang:lista')

    ordering = 'user__first_name'

    login_required = True

    extra_context = {
        'user_groups': apps.get_model('authentication.UserGroup').objects.filter(is_external=False),
        'nolle_groups': apps.get_model('authentication.NolleGroup').objects.all()
    }

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        try:
            self.happening = models.Happening.objects.get(pk=self.kwargs['pk'])
        except models.Happening.DoesNotExist:
            self.raise_exception = True
            self.handle_no_permission()

    def test_func(self):
        return self.happening.user_can_edit_happening(self.request.user.profile)

    def get_queryset(self):
        self.queryset = models.Registration.objects.filter(happening=models.Happening.objects.get(pk=self.kwargs['pk']))
        querryset = super().get_queryset()
        return querryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'happening': models.Happening.objects.get(pk=self.kwargs['pk']),
            'user_can_edit_registrations': self.request.user.has_perm(
                'nollesystemet.edit_user_registration') or self.request.user.profile in self.happening.editors.all(),
        })
        return context

class HappeningDownloadView(mixins.FohserietMixin, DownloadView):

    login_required = True

    def test_func(self):
        return self.happening.user_can_edit_happening(self.request.user.profile)

    csv_data_structure: Any = [
        {'title': 'Namn', 'accessor': 'user.name'},
        {'title': 'E-post', 'accessor': 'user.email'},
        {'title': 'nØllegrupp', 'accessor': 'user.nolle_group'},
        {'title': 'Speckost', 'accessor': 'food_preference'},
        {'title': 'Dryck', 'accessor': 'drink_option.drink'},
        {'title': 'Tillval', 'accessor': 'all_extra_options_str'},
        {'title': 'Övrigt', 'accessor': 'other'},
        {'title': 'Baspris', 'function': models.Registration.get_base_price},
        {'title': 'Dryckespris', 'function': models.Registration.get_drink_option_price},
        {'title': 'Tillvalspris', 'function': models.Registration.get_extra_option_price},
        {'title': 'Totalpris', 'function': models.Registration.get_full_price},
    ]

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.happening = models.Happening.objects.get(pk=self.kwargs['pk'])

    def get_file_name(self):
        return 'Anmalda_' + slugify(self.happening.name, allow_unicode=True).replace('-', '_').upper()

    def get_queryset(self):
        return models.Registration.objects.filter(happening=self.happening)


class HappeningUpdateView(mixins.HappeningOptionsMixin, mixins.FohserietMixin, UpdateView):
    model = models.Happening
    form_class = forms.HappeningForm

    template_name = 'fohseriet/evenemang/redigera.html'

    default_back_url = reverse_lazy('fohseriet:evenemang:lista')

    login_required = True
    success_url = default_back_url

    def post(self, request, *args, **kwargs):
        if 'delete' in request.POST:
            self.get_object().delete()
            return HttpResponseRedirect(self.get_back_url())
        else:
            return super(HappeningUpdateView, self).post(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        ret = super().get(request, *args, **kwargs)
        self.success_url = self.back_url
        return ret

    def test_func(self):
        return self.request.user.has_perm(
               'fohseriet.edit_user_registration') or (self.request.user.profile in models.Happening.objects.get(
               pk=self.kwargs['pk']).editors.all() if 'pk' in self.kwargs else True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        formset_kwargs = {}

        if self.request.POST:
            formset_kwargs['data'] = self.request.POST
        if self.object:
            formset_kwargs['instance'] = self.object

        context['drink_option_formset'] = forms.DrinkOptionFormset(**formset_kwargs)
        context['base_price_formset'] = forms.GroupBasePriceFormset(**formset_kwargs)
        context['extra_option_formset'] = forms.ExtraOptionFormset(**formset_kwargs)

        return context

    def get_object(self, queryset=None):
        if 'pk' not in self.kwargs:
            return None
        return super().get_object(queryset=queryset)
