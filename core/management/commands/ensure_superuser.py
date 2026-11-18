"""Create the first admin from env vars (DJANGO_SUPERUSER_USERNAME / _PASSWORD / _EMAIL) if none exists."""
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **opts):
        User = get_user_model()
        if User.objects.filter(is_superuser=True).exists():
            return
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
        if not (username and password):
            self.stderr.write("No superuser exists and DJANGO_SUPERUSER_USERNAME/PASSWORD are not set; skipping.")
            return
        User.objects.create_superuser(username, os.environ.get("DJANGO_SUPERUSER_EMAIL", ""), password)
        self.stdout.write(f"superuser '{username}' created")
