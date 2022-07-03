from typing import Callable, Any

from django.forms import Form
from django.urls import reverse_lazy, reverse
from django.utils.text import slugify
from django.views import View
from django.views.generic import UpdateView, ListView, FormView, TemplateView

import nollesystemet.models as models
import nollesystemet.forms as forms
import nollesystemet.mixins as mixins
from .misc import DownloadView, ModifiableModelFormView
from ..forms import HappeningPaymentUploadForm


class HappeningListViewFadderiet(mixins.FadderietMixin, ListView):
    model = models.Happening
    template_name = 'fadderiet/evenemang/index.html'

    ordering = 'start_time'

    login_required = True

    site_name = "Fadderiet: Evenemang"
    site_texts = ["intro", "betalningsinfo"]

    def get_queryset(self):
        self.queryset = models.Happening.objects.all()
        querryset = super().get_queryset()
        q_set = []
        for happening in querryset:
            if happening.is_visible_to(self.request.user.profile):
                happening_dict = {
                    'happening': happening,
                    'can_register': happening.can_register(self.request.user.profile),
                    'is_registered': happening.is_registered(self.request.user.profile),
                }
                try:
                    reg = models.Registration.objects.get(happening=happening, user=self.request.user.profile)
                except models.Registration.DoesNotExist:
                    happening_dict['base_price'] = happening.get_baseprice(
                        models.UserProfile.UserType(self.request.user.profile.user_type)
                    )
                    happening_dict['registration'] = None
                else:
                    happening_dict['base_price'] = None
                    happening_dict['registration'] = reg

                q_set.append(happening_dict)

        return q_set

class HappeningListViewFohseriet(mixins.FohserietMixin, ListView):
    model = models.Happening
    template_name = 'fohseriet/evenemang/index.html'

    ordering = 'start_time'

    login_required = True

    def test_func(self):
        return models.Happening.user_is_editor(self.request.user.profile) or \
               self.request.user.profile.has_perm('nollesystemet.edit_happening')

    def get_queryset(self):
        self.queryset = models.Happening.objects.all()
        querryset = super().get_queryset()
        return [{
            'happening': happening,
            'can_edit': happening.can_edit(self.request.user.profile),
            'can_see_registered': happening.can_see_registered(self.request.user.profile),
        }
            for happening in querryset
            if happening.can_edit(self.request.user.profile)
        ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'can_create': models.Happening.can_create(self.request.user.profile),
            'can_handle_payments': models.Happening.can_handle_payments(self.request.user.profile)
        })
        return context


class HappeningPaymentsView(mixins.FohserietMixin, FormView):
    form_class = HappeningPaymentUploadForm
    back_url = reverse_lazy('fohseriet:evenemang:lista')
    login_required = True
    template_name = "fohseriet/evenemang/betalningar.html"

    def test_func(self):
        return models.Happening.can_handle_payments(self.request.user.profile)

    def form_valid(self, form):
        new_payments = 0
        new_errors = 0
        error_indexes = []
        return_data = []

        if form.cleaned_data['swish']:
            return_data, new_payments, new_errors, error_indexes = self.handle_swish(form.cleaned_data['swish'])

        if form.cleaned_data['bankgiro']:
            return_data, new_payments, new_errors, error_indexes = self.handle_bankgiro(form.cleaned_data['bankgiro'])

        error_payments = []
        for error_index in error_indexes:
            error_payments.append({
                'OCR': return_data[error_index][4],
                'info': return_data[error_index][-1]
            })

        return self.render_to_response(
            self.get_context_data(
                form=form,
                success_message="Registrerade %d nya betalningar." % new_payments,
                error_message="Registrerade %d nya felaktiga betalningar." % new_errors if new_errors > 0 else None,
                error_payments=error_payments
            )
        )

    @staticmethod
    def handle_swish(swish_data):
        """ Datastruktur: Datum, Avsändare, Mobilnummer, Belopp, Meddelande"""
        new_payments = 0
        new_errors = 0
        error_indexes = []

        for i, entry_data in enumerate(swish_data):
            try:
                OCR_match = models.Registration.objects.get(OCR=entry_data[4].strip())

                paid_price = int(round(float(entry_data[3].replace(',', '.'))))
                if OCR_match.pre_paid_price == paid_price:
                    if not OCR_match.paid:
                        OCR_match.paid = True
                        OCR_match.save()
                        new_payments += 1

                    swish_data[i][4] = OCR_match.happening.name

                else:
                    new_errors += 1
                    swish_data[i].append("%s betalade %d,00, skulle betala %d,00" % (OCR_match.user.name, paid_price, OCR_match.pre_paid_price))
                    error_indexes.append(i)

            except models.Registration.DoesNotExist:
                pass

        return swish_data, new_payments, new_errors, error_indexes

    @staticmethod
    def handle_bankgiro(bankgiro_data):
        """ Datastruktur: Avsändare, Betalningsreferens, Bankgironummer, Belopp"""

        new_payments = 0
        new_errors = 0
        error_indexes = []

        for i, entry_data in enumerate(bankgiro_data):
            try:
                OCR_match = models.Registration.objects.get(OCR=entry_data[1].strip())

                paid_price = int(round(float(entry_data[3])))
                if OCR_match.pre_paid_price == paid_price:
                    if not OCR_match.paid:
                        OCR_match.paid = True
                        OCR_match.save()
                        new_payments += 1

                    bankgiro_data[i][1] = OCR_match.happening.name

                else:
                    new_errors += 1
                    bankgiro_data[i][1] = "FEL BELOPP! (%s)" % OCR_match.happening.name
                    error_indexes.append(i)

            except models.Registration.DoesNotExist:
                pass

        return bankgiro_data, new_payments, new_errors, error_indexes


class HappeningRegisteredListView(mixins.FohserietMixin, ListView):
    model = models.Registration
    template_name = 'fohseriet/evenemang/anmalda.html'

    back_url = reverse_lazy('fohseriet:evenemang:lista')

    ordering = 'user__first_name'

    login_required = True

    extra_context = {
        'user_types': models.UserProfile.UserType.names,
        'nolle_groups': models.NolleGroup.objects.all()
    }

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        try:
            self.happening = models.Happening.objects.get(pk=self.kwargs['pk'])
        except models.Happening.DoesNotExist:
            self.raise_exception = True
            self.handle_no_permission()

    def test_func(self):
        return self.happening.can_edit(self.request.user.profile)

    def get_queryset(self):
        self.queryset = models.Registration.objects.filter(happening=models.Happening.objects.get(pk=self.kwargs['pk']))
        querryset = super().get_queryset()
        return [{
            'registration': registration,
            'can_edit': registration.can_edit(self.request.user.profile),
            'can_see': registration.can_see(self.request.user.profile),
            'form': forms.RegistrationForm(instance=registration, editable=False)
        } for registration in querryset]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'happening': models.Happening.objects.get(pk=self.kwargs['pk']),
            'num_of_attendees_per_group': [
                {
                    'group': group.name,
                    'count': models.Registration.objects.filter(happening_id=self.kwargs['pk'], user__nolle_group_id=group.id).count()
                }
                for group in models.NolleGroup.objects.all()
            ]
        })
        return context


class HappeningDownloadView(mixins.FohserietMixin, DownloadView):

    login_required = True

    def test_func(self):
        return self.happening.can_edit(self.request.user.profile) or \
               self.happening.can_see_registered(self.request.user.profile)

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.happening = models.Happening.objects.get(pk=self.kwargs['pk'])
        self.csv_data_structure: Any = [
            {'title': 'Namn', 'accessor': 'user.name'},
            {'title': 'E-post', 'accessor': 'user.email'},
            {'title': 'nØllegrupp', 'accessor': 'user.nolle_group'},
            {'title': 'Användartyp', 'accessor': 'user.user_type'},
            {'title': 'Övrigt', 'accessor': 'other'},
            {'title': 'Förbetalningspris', 'accessor': 'pre_paid_price'},
            {'title': 'Pris på plats', 'accessor': 'on_site_paid_price'},
            {'title': 'Har betalat', 'accessor': 'paid'},
            {'title': 'Har deltagit', 'accessor': 'attended'},
        ]
        if self.happening.food:
            self.csv_data_structure.append({'title': 'Speckost', 'accessor': 'food_preference'})
        if self.happening.drinkoption_set.count() > 0:
            self.csv_data_structure.append({'title': 'Dryck', 'accessor': 'drink_option.drink'})
            self.csv_data_structure.append({'title': 'Dryckespris', 'accessor': 'drink_price'})
        if self.happening.extraoption_set.count() > 0:
            self.csv_data_structure.append({'title': 'Tillval', 'accessor': 'all_extra_options_str'})
            self.csv_data_structure.append({'title': 'Tillvalspris', 'accessor': 'extra_option_price'})

    def get_file_name(self):
        return 'Anmalda_' + slugify(self.happening.name, allow_unicode=True).replace('-', '_').upper()

    def get_queryset(self):
        return models.Registration.objects.filter(happening=self.happening)


class HappeningUpdateView(mixins.FohserietMixin, ModifiableModelFormView):
    model = models.Happening
    form_class = forms.HappeningForm
    editable = True
    deletable = True

    template_name = 'fohseriet/evenemang/redigera.html'
    back_url = reverse_lazy('fohseriet:evenemang:lista')
    login_required = True
    success_url = back_url

    def test_func(self):
        self.object = self.get_object()
        if self.object is None:
            return models.Happening.can_create(self.request.user.profile)
        else:
            return self.object.can_edit(self.request.user.profile)

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

    def get_initial(self):
        initial = super().get_initial()
        if self.object is None:
            initial['takes_registration'] = False
        return initial

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


class HappeningPaidAndPresenceView(mixins.FohserietMixin, TemplateView):
    template_name = "fohseriet/evenemang/narvaro.html"
    login_required = True

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        try:
            self.happening = models.Happening.objects.get(pk=self.kwargs['pk'])
        except models.Happening.DoesNotExist:
            self.handle_no_permission()

        self.back_url = reverse('fohseriet:evenemang:anmalda', kwargs={'pk': self.happening.pk})

    def test_func(self):
        return self.happening.can_edit(self.request.user.profile)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'happening': self.happening
        })
        return context


class HappeningConfirmView(mixins.FohserietMixin, TemplateView):
    template_name = "fohseriet/evenemang/bekrafta.html"
    login_required = True

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        try:
            self.happening = models.Happening.objects.get(pk=self.kwargs['pk'])
        except models.Happening.DoesNotExist:
            self.handle_no_permission()

        self.back_url = reverse('fohseriet:evenemang:anmalda', kwargs={'pk': self.happening.pk})

    def test_func(self):
        return self.happening.can_edit(self.request.user.profile)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'happening': self.happening,
            'unconfirmed_registrations': models.Registration.objects.filter(
                                             happening=self.happening, confirmed=False
                                         ).order_by('user__first_name')
        })
        return context
