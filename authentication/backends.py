from django.contrib.auth.backends import ModelBackend
from django.conf import settings
from cas import CASClient
from .models import AuthUser

class UserCredentialsBackend(ModelBackend):
    """
    Backend defining authentication for users using username and password. Inherits functionality from
    django.contrib.auth.backends.ModelBackend, but adds constraint of needing the correct backend setting in AuthUser
    (auth_backend = 'CRED').
    """

    def user_can_authenticate(self, user: AuthUser):
        return super().user_can_authenticate(user) and user.can_use_auth_method('CRED')


class CASBackend(ModelBackend):
    """
    Backend defining authentication for users using CAS login. Inherits permissions functionality from
    django.contrib.auth.backends.ModelBackend, but adds ticket validation of CAS tickets.
    Backend restricts to users with correct backend setting in AuthUser (auth_backend = 'CAS').
    """

    backend_name = 'CAS'

    def user_can_authenticate(self, user: AuthUser):
        return super().user_can_authenticate(user) and user.can_use_auth_method('CAS')

    def authenticate(self, request, ticket, service, **kwargs):
        """
        Method to verify CAS-tickets.

        :param request: HttpRequest to verification page.
        :param ticket: Ticket to verify (as string).
        :param service: Service url to use in verification.

        :returns user: User instance or None if not verified.
        """
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
            user = user_model.objects.get_by_natural_key(username)
        except user_model.DoesNotExist:
            user = None

        # If such a user does not exist, get or create
        # one with a deterministic, CAS username
        if not user:
            user = user_model.objects.create_user(username, None, **{'auth_backend': 'CAS'})

        return user and self.user_can_authenticate(user)