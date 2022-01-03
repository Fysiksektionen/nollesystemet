from django.conf import settings
from django.urls import path, include, reverse_lazy

import authentication.views as auth_views
import nollesystemet.views as views
from nollesystemet.api_views import user as api_views_user
from nollesystemet.api_views import registration as api_views_registration
from nollesystemet.api_views import campussafari as api_views_campussafari

login_urls = ([
    path('', views.LoginViewFohseriet.as_view(), name='index'),
    path('cred/', views.LoginCredentialsViewFohseriet.as_view(), name='cred'),
    path('cas/', auth_views.login.LoginCas.as_view(
        default_redirect_url=reverse_lazy('fohseriet:index'),
        default_fail_url=reverse_lazy('fohseriet:logga-in:index'),
        service_root_url=settings.DOMAIN_URL + "/fohseriet/logga-in/cas/"
    ), name='cas'),
], 'logga-in')

happening_urls = ([
    path('', views.HappeningListViewFohseriet.as_view(), name="lista"),
    path('skapa/', views.HappeningUpdateView.as_view(), name='skapa'),
    path('betalningar/', views.HappeningPaymentsView.as_view(), name="betalningar"),
    path('<int:pk>/redigera/', views.HappeningUpdateView.as_view(), name='redigera'),
    path('<int:pk>/anmalda/', views.HappeningRegisteredListView.as_view(), name='anmalda'),
    path('<int:pk>/ladda-ned-anmalda/', views.HappeningDownloadView.as_view(), name='ladda-ned-anmalda'),
    path('<int:pk>/narvaro/', views.HappeningPaidAndPresenceView.as_view(), name='narvaro'),
    path('<int:pk>/bekrafta-anmalda/', views.HappeningConfirmView.as_view(), name='bekrafta-anmalda'),
], 'evenemang')

user_urls = ([
    path('', views.UsersListView.as_view(), name="index"),
    path('skapa/', views.UserUpdateView.as_view(), name='skapa'),
    path('<int:pk>/redigera/', views.UserUpdateView.as_view(), name='redigera'),
    path('<int:pk>/anmalningar/', views.UserRegistrationsListView.as_view(), name='anmalningar'),
    path('<int:pk>/nolleenkaten/', views.UserNolleFormView.as_view(), name='nolleenkaten'),
], 'anvandare')

registration_urls = ([
    path('<int:pk>/redigera/', views.RegistrationUpdateView.as_view(), name="redigera"),
], 'anmalan')

nolle_form_urls = ([
    path('', views.NolleFormManageView.as_view(), name="index"),
    path('ladda-ned-svar/', views.NolleFormDownloadView.as_view(), name="ladda-ned-svar"),
], 'nolleenkaten')

api_urls = ([
    path('user_profiles/<int:pk>', api_views_user.get_user_profile_form_HTML),
    path('registrations', api_views_registration.RegistrationList.as_view()),
    path('registrations/<int:pk>', api_views_registration.update_registration),
    path('registrations/<int:pk>/confirm', api_views_registration.confirm_registration),
    path('campussafari/<int:group_pk>/check-side-quest/<int:side_pk>', api_views_campussafari.check_side_quest),
    path('campussafari/<int:group_pk>/set-station-points/<int:station_pk>', api_views_campussafari.set_station_points)
], 'api')

campussafari_urls = ([
    path('stationer/', views.FohserietStationAdministration.as_view()),
    path('sidouppdrag/', views.FohserietSideQuestAdministration.as_view())
], 'campussafari')

fohseriet_urls = ([
    path('', views.misc.FohserietIndexView.as_view(), name='index'),
    path('saknar-rattigheter/', views.misc.AccessDeniedViewFohseriet.as_view(), name='saknar-rattigheter'),
    path('logga-in/', include(login_urls)),
    path('logga-ut/', views.authentication.LogoutViewFohseriet.as_view(), name='logga-ut'),
    path('evenemang/', include(happening_urls)),
    path('anvandare/', include(user_urls)),
    path('anmalan/', include(registration_urls)),
    path('nolleenkaten/', include(nolle_form_urls)),
    path('campussafari/', include(campussafari_urls)),
    path('<path:url>/', views.FohserietMenuView.as_view(
        template_name="fohseriet/sidan-finns-inte.html"
    ), name="sidan-finns-inte"),
    path('api/', include(api_urls)),
], 'fohseriet')
