import os
import pytz
import logging
from django.contrib.sites.shortcuts import get_current_site
from django.utils import timezone
from django.conf import settings
from configuration import models
from django.shortcuts import redirect
from django.urls import reverse_lazy
from core import VERSION


class CustomAMSMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.version = VERSION
        site = get_current_site(request)
        general = models.SiteSettings.objects.filter(site=site).first()
        if general:
            request.user_bar = general.user_bar
            if general.under_construction:
                if not (request.path == reverse_lazy("construction") or
                        request.path == reverse_lazy('auth_login') or
                        request.user.is_superuser):
                    return redirect('construction')
        if not settings.EMAIL_HOST_PASSWORD:
            try:
                auth_config(site)
            except Exception as e:
                logging.error(e)
        request.email = settings.DEFAULT_FROM_EMAIL or "None"
        if general:
            if general.timezone:
                request.user_bar = general.user_bar
                settings.TIME_ZONE = general.timezone
                settings.USER_LOGS = general.user_logs or True
            timezone.activate(
                pytz.timezone(general.timezone or settings.TIME_ZONE)
            )
        else:
            timezone.activate(pytz.timezone(settings.TIME_ZONE))
        return self.get_response(request)


def auth_config(site):
    if getattr(settings, 'ACCOUNT_ACTIVATION_DAYS', None) is None:
        _auth_config = models.AuthenticationSettings.objects.filter(
            site=site
        ).first()
        if _auth_config:
            settings.ACCOUNT_ACTIVATION_DAYS = _auth_config.activation_days
            settings.REGISTRATION_AUTO_LOGIN = _auth_config.registration_auto_login  # noqa
            settings.SEND_ACTIVATION_EMAIL = _auth_config.send_activation_email
            settings.REGISTRATION_OPEN = _auth_config.registration_open
