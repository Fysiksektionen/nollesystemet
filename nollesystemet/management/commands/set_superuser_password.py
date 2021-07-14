from django.core.management.base import BaseCommand
import authentication.models as auth_models


class Command(BaseCommand):
    help = "Updates the superuser admin's password according to the first argument."

    def add_arguments(self, parser):
        parser.add_argument('password', nargs=1, type=str)

    def handle(self, *args, **options):
        try:
            admin = auth_models.AuthUser.objects.get(is_superuser=True, username='admin')
            admin.set_password(options['password'][0])
            admin.save()
        except auth_models.AuthUser.DoesNotExist:
            self.stdout.write("No superuser found.")

        self.stdout.write(self.style.SUCCESS("Password updated!"))
