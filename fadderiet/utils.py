from urllib.parse import urlencode

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.http import HttpResponseRedirect
from django.urls import reverse

menu_item_info = {
    'index': {
        'name': 'Hem',
        'url_name': 'fadderiet:index',
        'align': 'left',
        'user': 'any',
    },
    'schema': {
        'name': 'Schema',
        'url_name': 'fadderiet:schema',
        'align': 'left',
        'user': 'any',
    },
    'bra-info': {
        'name': 'Bra info',
        'url_name': 'fadderiet:bra-info',
        'align': 'left',
        'user': 'any',
    },
    'om-fadderiet': {
        'name': 'Om fadderiet',
        'url_name': 'fadderiet:om-fadderiet',
        'align': 'left',
        'user': 'any',
    },
    'anmal-dig': {
        'name': 'Anmäl dig',
        'url_name': 'fadderiet:anmal-dig',
        'align': 'left',
        'user': 'any',
    },
    'kontakt': {
        'name': 'Kontakt',
        'url_name': 'fadderiet:kontakt',
        'align': 'left',
        'user': 'any',
    },
    'mina-sidor': {
        'name': 'Mina sidor',
        'url_name': 'fadderiet:mina-sidor',
        'align': 'right',
        'user': 'logged-in',
    },
    'mina-sidor:profil': {
        'name': 'Min profil',
        'url_name': 'fadderiet:mina-sidor:profil',
        'align': 'right',
        'user': 'logged-in',
    },
    'logga-in': {
        'name': 'Logga in',
        'url_name': 'fadderiet:logga-in:index',
        'align': 'right',
        'user': 'logged-out',
    },
    'logga-ut': {
        'name': 'Logga ut',
        'url_name': 'fadderiet:logga-ut',
        'align': 'right',
        'user': 'logged-in',
    },
}


def custom_redirect(url_name, *args, **kwargs):
    url = reverse(url_name, args=args)
    params = urlencode(kwargs)
    print(url + "?%s" % params)
    return HttpResponseRedirect(url + "?%s" % params)


def make_crispy_form(form_class, submit_button=None, form_action=None):
    class CrispyForm(form_class):
        def __init__(self, *args, **kwargs):
            self.helper = FormHelper()
            self.helper.form_method = 'post'
            self.helper.add_input(Submit('submit', submit_button or 'Submit'))
            self.helper.form_action = form_action or ''
            super().__init__(*args, **kwargs)

    return CrispyForm