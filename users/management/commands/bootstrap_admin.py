from django.core.management.base import BaseCommand

from users.bootstrap import (
    DEFAULT_ADMIN_EMAIL,
    DEFAULT_ADMIN_PASSWORD,
    DEFAULT_ADMIN_USERNAME,
    ensure_bootstrap_admin_user,
)


class Command(BaseCommand):
    help = 'Create or reset the fallback admin account for local recovery.'

    def add_arguments(self, parser):
        parser.add_argument('--username', default=DEFAULT_ADMIN_USERNAME)
        parser.add_argument('--password', default=DEFAULT_ADMIN_PASSWORD)
        parser.add_argument('--email', default=DEFAULT_ADMIN_EMAIL)

    def handle(self, *args, **options):
        import os

        os.environ['BOOTSTRAP_ADMIN_ENABLED'] = 'true'
        os.environ['BOOTSTRAP_ADMIN_USERNAME'] = options['username']
        os.environ['BOOTSTRAP_ADMIN_PASSWORD'] = options['password']
        os.environ['BOOTSTRAP_ADMIN_EMAIL'] = options['email']

        user = ensure_bootstrap_admin_user(force=True)
        self.stdout.write(
            self.style.SUCCESS(
                f'Bootstrap admin ready: {user.username}'
            )
        )
