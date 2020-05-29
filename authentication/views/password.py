import django.contrib.auth.views as auth_views
from django.urls import reverse, reverse_lazy


class PasswordResetView(auth_views.PasswordResetView):
    email_template_name = 'authentication/password_reset_email.html'
    subject_template_name = 'authentication/password_reset_subject.txt'
    success_url = reverse_lazy('authentication:password_reset_done')
    template_name = 'authentication/password_reset_form.html'


class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    success_url = reverse_lazy('authentication:password_reset_complete')
    template_name = 'authentication/password_reset_confirm.html'


class PasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'authentication/password_reset_done.html'


class PasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'authentication/password_reset_complete.html'


class PasswordChangeView(auth_views.PasswordChangeView):
    success_url = reverse_lazy('authentication:password_change_done')
    template_name = 'authentication/password_change_form.html'


class PasswordChangeDoneView(auth_views.PasswordChangeDoneView):
    template_name = 'authentication/password_change_done.html'
