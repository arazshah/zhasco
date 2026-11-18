"""Create the first dashboard admin if none exists.

Username/password default to admin / DEFAULT_PASSWORD (override with DJANGO_SUPERUSER_USERNAME /
DJANGO_SUPERUSER_PASSWORD). The bootstrap password must be changed at the first login.
"""
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from core.models import InitialPassword

DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "ZhAS-Change-Me-1405"


class Command(BaseCommand):
    def handle(self, *args, **opts):
        User = get_user_model()
        if User.objects.filter(is_superuser=True).exists():
            return
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME") or DEFAULT_USERNAME
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD") or DEFAULT_PASSWORD
        user = User.objects.create_superuser(username, os.environ.get("DJANGO_SUPERUSER_EMAIL", ""), password)
        InitialPassword.objects.create(user=user, password_hash=user.password)
        self.stdout.write(f"superuser '{username}' created; password must be changed at first login")
