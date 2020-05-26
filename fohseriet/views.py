from django.http import HttpResponseRedirect
from django.shortcuts import render, HttpResponse, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView, CreateView
from .forms import *
from .models import *
from .mixins import *

def index(request, *args, **kwargs):
    template_name = 'fohseriet/index.html'
    heading = 'Startsida för Föhseriets hemsida'
    text = 'Det här är det som så småningom kommer att bli en förklarande text för hur hemsidan fungerar.'
    return render(request, template_name, {'heading': heading, 'text': text})



#This one needs to be updated to look more like the CreateView.
class HappeningUpdateView(UpdateView, HappeningOptionsMixin):
    model = Happening
    fields = '__all__'
    template_name = 'fohseriet/create_happening.html'
    success_url = reverse_lazy('fohseriet:happening-list')

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



class HappeningListView(ListView):
    model = Happening
    template_name = 'fohseriet/happening_list.html'
