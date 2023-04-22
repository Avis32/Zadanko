from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from user_anonymizer.anonymizers import UserAnonymizer


class Command(BaseCommand):
    help = "Anonymizes User"

    def add_arguments(self, parser):
        parser.add_argument("user_pk", nargs="+", type=int)

    def handle(self, *args, **options):
        user_pk = options["user_pk"][0]
        user = User.objects.get(pk=user_pk)
        anonymizer = UserAnonymizer(instance=user)
        anonymizer.anonymize()
        self.stdout.write(
            self.style.SUCCESS('Successfully anonymized user "%s"' % user_pk)
        )
