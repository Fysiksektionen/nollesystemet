import django.contrib.auth.views as auth_views
from django.http import QueryDict
from django.urls import reverse, reverse_lazy
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import REDIRECT_FIELD_NAME

class PasswordResetView(auth_views.PasswordResetView):
    email_template_name = 'authentication/password_reset_email.html'
    subject_template_name = 'authentication/password_reset_subject.txt'
    success_url = reverse_lazy('authentication:password_reset_done')
    template_name = 'authentication/password_reset_form.html'

    def get(self, request, *args, **kwargs):
        auth_logout(request)
        return super().get(request, *args, **kwargs)


class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    success_url = reverse_lazy('authentication:password_reset_complete')
    template_name = 'authentication/password_reset_confirm.html'


class PasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'authentication/password_reset_done.html'

    def get(self, request, *args, **kwargs):
        auth_logout(request)
        return super().get(request, *args, **kwargs)


class PasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'authentication/password_reset_complete.html'

    def get(self, request, *args, **kwargs):
        auth_logout(request)
        return super().get(request, *args, **kwargs)


class PasswordChangeView(auth_views.PasswordChangeView):
    success_url = reverse_lazy('authentication:password_change_done')
    template_name = 'authentication/password_change_form.html'

    def get_success_url(self):
        success_url = super(PasswordChangeView, self).get_success_url()
        return success_url + '?success=True'

class PasswordChangeDoneView(auth_views.PasswordChangeDoneView):
    template_name = 'authentication/password_change_done.html'

    def get(self, request, *args, **kwargs):
        auth_logout(request)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
           'password_changed': self.request.GET.get('success', None) is not None
        })
        return context

