import json

from django.contrib.staticfiles import finders
from django.core.management.base import BaseCommand, CommandError
import django.contrib.auth.models as django_auth_models
import authentication.models as auth_models
from nollesystemet.models import *

class Command(BaseCommand):
    """
    1) Create administrative groups and assign correct privileges.
    2) Check that a superuser with username 'admin' exists. Else create one. Assign authenticaiton groups.
    3) Create NolleGroups.
    """

    help = 'Restores all models to the given minimum requirements. Does not delete other stuff.'

    def handle(self, *args, **options):

        authentication_groups = []
        nolle_groups = []

        # 1) Create administrative groups and assign correct privileges.
        with open(finders.find('resources/groups.json')) as json_file:
            data = json.load(json_file)
            for group_info in data['groups']:
                try:
                    group = auth_models.Group.objects.get(name=group_info['name'])
                except django_auth_models.Group.DoesNotExist:
                    group = auth_models.Group(name=group_info['name'])
                    group.save()
                authentication_groups.append(group)

                for perm_codename in group_info['perms']:
                    try:
                        perm = django_auth_models.Permission.objects.get(codename=perm_codename)
                        if perm not in group.permissions.all():
                            group.permissions.add(perm)
                    except django_auth_models.Permission.DoesNotExist:
                        self.stdout.write('Permission %s was not found and not loaded.' % perm_codename)

        # 2) Check that a superuser with username 'admin' exists. Else create one. Assign authenticaiton groups.
        try:
            admin = UserProfile.objects.get(auth_user__username='admin')
            admin.auth_user.is_staff = True
            admin.auth_user.is_superuser = True
            admin.auth_user.save()
        except UserProfile.DoesNotExist:
            admin = UserProfile.objects.create_superuser(username='admin',
                                                         password=None,
                                                         email='nollesystemet@f.kth.se',
                                                         first_name="Admin",
                                                         last_name="Superuser"
                                                         )

        for group in authentication_groups:
            if group not in admin.auth_user.groups.all():
                admin.auth_user.groups.add(group)


        # 3) Create NolleGroups.
        with open(finders.find('resources/nolle_groups.json')) as json_file:
            data = json.load(json_file)
            for group_info in data['nolle_groups']:
                try:
                    nolle_group = NolleGroup.objects.get(name=group_info['name'])
                except NolleGroup.DoesNotExist:
                    nolle_group = NolleGroup(name=group_info['name'])
                    nolle_group.save()
                nolle_groups.append(nolle_group)

        # 4) Create Singeltons
        HappeningInfo.load()

        # inf) End.
        if not ('print' in options and not options['print']):
            self.stdout.write(self.style.SUCCESS('Successfully re-initialized system!'))

