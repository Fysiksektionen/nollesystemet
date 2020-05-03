from django.http import HttpResponseRedirect
from django.shortcuts import render, HttpResponse, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView, CreateView
from .forms import *
from .models import *

def index(request, *args, **kwargs):
    template_name = 'fohseriet/index.html'
    heading = 'Startsida för Föhseriets hemsida'
    text = 'Det här är det som så småningom kommer att bli en förklarande text för hur hemsidan fungerar.'
    return render(request, template_name, {'heading': heading, 'text': text})


#This one needs to be updated to look more like the CreateView.
class HappeningUpdateView(UpdateView):
    model = Happening
    fields = '__all__'
    template_name = 'fohseriet/edit_happening.html'
    success_url = reverse_lazy('fohseriet:happening-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['drink_options'] = DrinkOption.objects.all()
        return context


class HappeningCreateView(CreateView):
    model = Happening
    success_url = reverse_lazy('fohseriet:happening-list')
    fields = '__all__'
    template_name = 'fohseriet/create_happening.html'

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

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        form = super().get_form(form_class)
        form.fields['start_time'].widget = forms.SelectDateWidget()
        form.fields['end_time'].widget = forms.SelectDateWidget()
        return form

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


class HappeningListView(ListView):
    model = Happening
    template_name = 'fohseriet/happening_list.html'
