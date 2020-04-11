from django.http import HttpResponseRedirect
from django.shortcuts import render, HttpResponse
from django.urls import reverse
from django.views import View
from .forms import *
from .models import *

def hello_world(request, *args, **kwargs):
    return HttpResponse("Hello world!\n You are at: " + request.get_full_path_info())

class TestFormsView(View):
    form_class = None
    initial = {}
    template_name = 'fohseriet/redigera_evenemang.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(reverse('fohseriet:start'))
        return render(request, self.template_name, {'form': form})



