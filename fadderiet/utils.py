from urllib.parse import urlencode

from django.http import HttpResponseRedirect
from django.urls import reverse

menu_item_info = {
    'index': {
        'name': 'Hem',
        'url_name': 'fadderiet:index',
        'align': 'left',
    },
    'schema': {
        'name': 'Schema',
        'url_name': 'fadderiet:schema',
        'align': 'left',
    },
    'bra_info': {
        'name': 'Bra info',
        'url_name': 'fadderiet:bra_info',
        'align': 'left',
    },
    'om_fadderiet': {
        'name': 'Om fadderiet',
        'url_name': 'fadderiet:om_fadderiet',
        'align': 'left',
    },
    'anmal_dig': {
        'name': 'Anmäl dig',
        'url_name': 'fadderiet:anmal_dig',
        'align': 'left',
    },
    'kontakt': {
        'name': 'Kontakt',
        'url_name': 'fadderiet:kontakt',
        'align': 'left',
    },
    'mina_sidor': {
        'name': 'Mina sidor',
        'url_name': 'fadderiet:mina_sidor',
        'align': 'right',
    },
    'logga-in': {
        'name': 'Logga in',
        'url_name': 'fadderiet:logga-in',
        'align': 'right',
    },
}


def custom_redirect(url_name, *args, **kwargs):
    url = reverse(url_name, args=args)
    params = urlencode(kwargs)
    print(url + "?%s" % params)
    return HttpResponseRedirect(url + "?%s" % params)