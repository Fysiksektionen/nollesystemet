from django.core.management.base import BaseCommand, CommandError
import authentication.models as auth_models
from nollesystemet.models import *

from .re_initialize_nollesystemet import Command as ReInitializeCommand

class Command(BaseCommand):
    help = 'Full reset of database. Deletes everything and initializes the minimum requirements.'

    re_initialize_command = ReInitializeCommand()

    def handle(self, *args, **options):

        UserProfile.objects.all().delete()
        Happening.objects.all().delete()

        auth_models.AuthUser.objects.all().delete()
        auth_models.Group.objects.all().delete()

        NolleFormAnswer.objects.all().delete()
        DynamicNolleFormQuestion.objects.all().delete()

        self.re_initialize_command.handle(*args, **options, print=False)
        if not ('print' in options and not options['print']):
            self.stdout.write(self.style.SUCCESS('Successfully reset system!'))
