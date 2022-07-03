from django import template
from django.conf import settings

register = template.Library()

@register.simple_tag
def get_setting(settings_name):
    if isinstance(settings_name, str):
        try:
            return settings.__getattr__(settings_name)
        except AttributeError as e:
            pass
    return ""
