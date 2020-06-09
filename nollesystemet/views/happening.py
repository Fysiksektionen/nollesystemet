from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.views.generic import UpdateView, ListView

import nollesystemet.models as models
import nollesystemet.forms as forms
import nollesystemet.mixins as mixins


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

class HappeningUpdateView(mixins.FohserietMixin, UpdateView):
    model = models.Happening
    form_class = forms.HappeningForm

    template_name = 'fohseriet/evenemang/redigera.html'

    default_back_url = reverse_lazy('fohseriet:evenemang:lista')

    login_required = True

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.success_url = self.back_url

    def post(self, request, *args, **kwargs):
        if 'delete' in request.POST:
            self.get_object().delete()
            return HttpResponseRedirect(self.get_back_url())
        else:
            return super(HappeningUpdateView, self).post(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        ret = super().get(request, *args, **kwargs)
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

    def form_valid(self, form):
        context = self.get_context_data(form=form)
        drink_option_formset = context['drink_option_formset']
        base_price_formset = context['base_price_formset']
        extra_option_formset = context['extra_option_formset']
        if drink_option_formset.is_valid() and base_price_formset.is_valid() and extra_option_formset.is_valid():
            response = super().form_valid(form)

            drink_option_formset.instance = self.object
            drink_option_formset.save()

            base_price_formset.instance = self.object
            base_price_formset.save()

            extra_option_formset.instance = self.object
            extra_option_formset.save()
            return response
        else:
            return super().form_invalid(form)