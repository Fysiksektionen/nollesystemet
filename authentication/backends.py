from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.db import models
from django.conf import settings
from django.db.models import Q, QuerySet
from cas import CASClient
from django.contrib.auth.models import Permission

from .models import AuthUser

class UserCredentialsBackend(ModelBackend):
    """ Backend defining authentication for users using username and password. """

    backend_name = 'CRED'

    def user_can_authenticate(self, user: AuthUser):
        """ Restricts authentication to users with correct backend setting in AuthUser. """

        return super().user_can_authenticate(user) and user.can_use_auth_method(self.backend_name)


class CASBackend(ModelBackend):
    """ Backend defining authentication for users using CAS login. """

    backend_name = 'CAS'

    def user_can_authenticate(self, user: AuthUser):
        """ Restricts authentication to users with correct backend setting in AuthUser. """

        return super().user_can_authenticate(user) and user.can_use_auth_method(backend_name=self.backend_name)

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
                           server_url=settings.CAS_SERVER_URL)
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
            # If such a user does not exist, get or create.
            if settings.CREATE_USER_IF_MISSING_CAS:
                # TODO: Create a user with a profile.
                user = user_model.objects.create_user(username, None, **{'auth_backend': self.backend_name})
            else:
                user = None

        return user and self.user_can_authenticate(user)


class FakeCASBackend(CASBackend):
    """ Fake backend authorizing simple fake tickets """

    def authenticate(self, request, ticket, service, **kwargs):
        """
        Authenticates a fake ticket containing the user's username. Uses the following rules:
            - Returns matching user if username exists.
            - if settings.CREATE_USER_IF_MISSING_CAS:
                Creates and return user if username is missing.
              else:
                Returns None.
        """
        user_model = AuthUser

        # Try to find user
        try:
            user = user_model.objects.get_by_natural_key(ticket)
        except user_model.DoesNotExist:
            # If such a user does not exist, get or create
            if settings.CREATE_USER_IF_MISSING_CAS:
                # TODO: Create a user with a profile.
                user = user_model.objects.create_user(ticket, None, **{'auth_backend': self.backend_name})
            else:
                user = None

        return user and self.user_can_authenticate(user)


class MultipleGroupCategoriesBackend(ModelBackend):
    def authenticate(self, *args, **kwargs):
        return None

    def user_can_authenticate(self, user):
        return False

    def _get_group_permissions(self, user_obj):
        user_model = get_user_model()

        # If list of groups exist, is not None and not empty
        if hasattr(user_model, 'PERMISSION_GROUPS') and user_model.PERMISSION_GROUPS and len(user_model.PERMISSION_GROUPS) != 0:
            query = Q()

            # For all fields in the list
            for group_type_name in user_model.PERMISSION_GROUPS:
                group_field = getattr(user_obj, group_type_name)

                # If group_field is an instance of Group (or subclass)
                if isinstance(group_field, Group):
                    query = query | Q(**{'group': group_field})

                # Else assume that it's a many-to-many relation so you are dealing with a manager.
                else:
                    list_of_groups = None
                    try:
                        list_of_groups = group_field.all()
                    except:
                        raise Exception("%s is not an acceptable field for permission handling." % group_type_name)

                    for group in list_of_groups:
                        # If group_field is an instance of Group (or subclass)
                        if isinstance(group, Group):
                            query = query | Q(**{'group': group})
                        else:
                            raise Exception("%s is not an acceptable field for permission handling." % group_type_name)

            return Permission.objects.filter(query)
        else:
            return Permission.objects.none()
