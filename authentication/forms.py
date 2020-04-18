import django.forms as forms
from django.contrib.auth.forms import UsernameField

class FakeCASLoginForm(forms.Form):
    username = UsernameField()
