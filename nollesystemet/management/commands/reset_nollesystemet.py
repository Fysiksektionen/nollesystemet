from nollesystemet.models import *

from .re_initialize_nollesystemet import Command as ReInitializeCommand

class Command(ReInitializeCommand):
    help = 'Full reset of database. Deletes everything and initializes the minimum requirements.'

    models = [UserProfile, Happening, auth_models.AuthUser, auth_models.Group, DynamicNolleFormQuestion]

    def handle(self, *args, **options):
        for model in self.models:
            try:
                model.objects.all().delete()
            except:
                self.stdout.write(self.style.SUCCESS('Successfully reset system!'))

        super().handle(*args, **options, print=False)
        self.stdout.write(self.style.SUCCESS('Successfully reset system!'))
