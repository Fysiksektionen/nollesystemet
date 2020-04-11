from django.contrib.auth.backends import BaseBackend, ModelBackend
from django.conf import settings
from cas import CASClient
from .models import AuthUser, UserProfile

class UserCredentialsBackend(ModelBackend):
    def user_can_authenticate(self, user: AuthUser):
        return super().user_can_authenticate(user) and user.auth_backend == 'DJANGO'


class KTHBackend(ModelBackend):
    """
    Authentication backend that verifies A CAS ticket.
    Mainly copied from Uniauth.
    """

    def authenticate(self, request, ticket, service, **kwargs):
        user_model = AuthUser

        # Attempt to verify the ticket with the institution's CAS server
        client = CASClient(version=2, service_url=service,
                           server_url=settings.KTH_CAS_SERVER_URL)
        username, attributes, pgtiou = client.verify_ticket(ticket)

        # Add the attributes returned by the CAS server to the session
        if request and attributes:
            request.session['attributes'] = attributes

        # If no username was returned, verification failed
        if not username:
            return None

        # Try to find user
        try:
            user = user_model.objects.get(kth_id=username)
        except user_model.DoesNotExist:
            user = None

        # If such a user does not exist, get or create
        # one with a deterministic, CAS username
        if not user:
            temp_username = "cas-%s-%s" % ('kth', username)
            user, created = user_model._default_manager.get_or_create(
                **{user_model.USERNAME_FIELD: temp_username,
                   'kth_id': username,
                   'auth_backend': 'CAS'})

        return user and user.auth_backend == 'CAS'
