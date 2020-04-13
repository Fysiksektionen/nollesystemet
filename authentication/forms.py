import django.forms as forms
from django.contrib.auth.forms import AuthenticationForm, UsernameField

class CredAuthenticationForm(AuthenticationForm):
    pass

class FakeCASLoginForm(forms.Form):
    username = UsernameField()


# TODO: Write authentication and user related forms
# Authenticate using credentials
# Create user form
# Alter user form
# Password reset form
# Password set form
# Password change form
