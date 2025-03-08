import os
import logging
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    def handle(self, *args, **options):
        email = os.getenv('SUPERUSER_EMAIL', 'admin@gmail.com')
        password = os.getenv('SUPERUSER_PASSWORD', 'admin')

        if not get_user_model().objects.filter(email=email).exists():
            get_user_model().objects.create_superuser(
                email=email, password=password
            )
            logging.info(
                f'Admin initialized with email:{email} & password:{password}'
            )
        else:
            logging.warning(
                'Admin account has already been initialized.'
            )
