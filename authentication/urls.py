import django.contrib.auth.views as auth_views
from django.urls import path
from django.views.generic import TemplateView

import authentication.views as views

app_name = 'authentication'
urlpatterns = [
    path('', TemplateView.as_view(template_name="authentication/index.html"), name='index'),

    path('login/', views.Login.as_view(), name="login"),
    path('login/cred/', views.LoginCred.as_view(), name="login_cred"),
    path('login/cas/', views.LoginCas.as_view(), name="login_cas"),

    path('logout/', auth_views.LogoutView.as_view(template_name="authentication/logged_out.html"), name="logout"),

    path('request_info/', TemplateView.as_view(template_name='authentication/print_get_post.html'), name='request_info'),

    path('password_change/', views.PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', views.PasswordChangeDoneView.as_view(), name='password_change_done'),

    path('password_reset/', views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('cas_fake/', views.FakeCASLogin.as_view(), name='fake_cas'),
    path('cas_fake/login/', views.FakeCASLogin.as_view(), name='fake_cas_login'),
    path('cas_fake/logout/', views.FakeCASLogout.as_view(), name='fake_cas_logout'),
    path('create_user/', views.AuthUserCreate.as_view(), name='auth_user_create'),
]