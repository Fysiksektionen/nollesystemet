from django.core.management.base import BaseCommand, CommandError
from nollesystemet.models import *

from .re_initialize_nollesystemet import Command as ReInitializeCommand

class Command(ReInitializeCommand):
    help = 'Full reset of database. Deletes everything and initializes the minimum requirements.'

    def handle(self, *args, **options):
        UserProfile.objects.all().delete()
        Happening.objects.all().delete()

        auth_models.AuthUser.objects.all().delete()
        auth_models.Group.objects.all().delete()

        NolleFormAnswer.objects.all().delete()
        DynamicNolleFormQuestion.objects.all().delete()

        super().handle(*args, **options, print=False)
        if not ('print' in options and not options['print']):
            self.stdout.write(self.style.SUCCESS('Successfully reset system!'))
