from django.contrib.auth.models import Permission
from django.core.management.base import BaseCommand

from authentication.models import AuthUser
from nollesystemet.models import *

class Command(BaseCommand):
    help = 'Initializes database with admin, user_groups and nolle_groups and more.'

    def handle(self, *args, **kwargs):

        # Create user groups
        user_groups = [
            {
                'name': 'nØllan'
            },
            {
                'name': 'Fadder'
            },
            {
                'name': 'Senior',
                'is_external': True,
             },
            {
                'name': 'Annan sektion',
                'is_external': True,
            },
            {
                'name': 'Administratör',
                'is_administrational': True,
                'permissions': ['edit_user_info', 'edit_user_registration'],
            },
            {
                'name': 'Arrangör',
                'is_administrational': True,
                'permissions': ['edit_happening'],
            },
        ]

        for group_info in user_groups:
            permissions = None
            if 'permissions' in group_info:
                permissions = group_info.pop('permissions')
            user_group = auth_models.UserGroup.objects.create(**group_info)
            if permissions:
                user_group.permissions.set(Permission.objects.filter(codename__in=permissions))

        # Create nolle groups
        nolle_groups = [
            {'name': 'A#'},
            {'name': 'Attans Bananer'},
            {'name': 'Fløwer Pøwer'},
            {'name': 'RTLL'},
            {'name': 'Sällskapsresan'},
            {'name': 'WoodstØck'},
        ]

        for group_info in nolle_groups:
            nolle_group = auth_models.NolleGroup.objects.create(**group_info)

        # Create superuser
        superuser = AuthUser.objects.create_superuser(
            username="admin",
            email="admin@f.kth.se",
            password='loser565'
        )
        superuser.user_group.set(auth_models.UserGroup.objects.filter(is_external=False, is_administrational=True))
