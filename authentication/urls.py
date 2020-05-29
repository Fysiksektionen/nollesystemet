import django.contrib.auth.views as auth_views
from django.urls import path
from django.views.generic import TemplateView

import authentication.views as views

app_name = 'authentication'
urlpatterns = [
    path('', TemplateView.as_view(template_name="authentication/index.html"), name='index'),

    path('login/', views.login.Login.as_view(), name="login"),
    path('login/cred/', views.login.LoginCred.as_view(), name="login_cred"),
    path('login/cas/', views.login.LoginCas.as_view(), name="login_cas"),

    path('logout/', auth_views.LogoutView.as_view(template_name="authentication/logged_out.html"), name="logout"),

    path('request_info/', TemplateView.as_view(template_name='authentication/print_get_post.html'), name='request_info'),

    path('password_change/', views.password.PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', views.password.PasswordChangeDoneView.as_view(), name='password_change_done'),

    path('password_reset/', views.password.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', views.password.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.password.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', views.password.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('cas_fake/', views.login.FakeCASLogin.as_view(), name='fake_cas'),
    path('cas_fake/login/', views.login.FakeCASLogin.as_view(), name='fake_cas_login'),
    path('cas_fake/logout/', views.login.FakeCASLogout.as_view(), name='fake_cas_logout'),

    path('create_user/', views.user.AuthUserCreateView.as_view(), name='auth_user_create'),
    path('update_user_profile/<pk>', views.user.UserProfileUpdateView.as_view(), name='update_user_profile'),
    path('update_auth_user/<pk>', views.user.AuthUserUpdateView.as_view(), name='update_auth_user'),
]