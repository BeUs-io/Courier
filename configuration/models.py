from django.db import models
from django.contrib.sites.models import Site
from django.utils.translation import gettext as _
from core.utils.utils import timezone_pytz
from core.base.model import BaseModel


class SiteSettings(BaseModel):
    updated_at = None
    created_at = None
    default_message = "We are doing important maintenance work on the website and will be back shortly. " \
                      "We apologise for any inconvenience caused. If you need to get in touch with us, " \
                      "please use one of the options below:"  # noqa
    logo = models.ImageField(
        upload_to='site/logo/', verbose_name=_("Logo"), null=True, blank=True
    )
    favicon = models.ImageField(
        upload_to='site/favicon/', verbose_name=_("Favicon"),
        null=True, blank=True
    )
    timezone = models.CharField(
        max_length=40, verbose_name=_("Timezone"), choices=timezone_pytz,
        default="Asia/Karachi", null=True, blank=True
    )
    color = models.CharField(max_length=10, null=True, default="#15a362")
    site = models.OneToOneField(
        to=Site, on_delete=models.CASCADE, related_name='site_general'
    )
    under_construction = models.BooleanField(
        default=False, help_text="on enable only super user access the site."
    )
    user_bar = models.BooleanField(
        default=True, help_text="enable or disable user bar."
    )
    user_logs = models.BooleanField(
        default=True,
        help_text="users logs enable (only super user can view users logs).",
        verbose_name="Users Logs"
    )
    message = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "general_settings"
        verbose_name = _("General Settings")
        verbose_name_plural = _("General Settings")

    def get_message(self):
        if not self.message:
            return SiteSettings.default_message
        return self.message

    def __str__(self):
        return "General Settings"


class SocialSetting(BaseModel):
    updated_at = None
    created_at = None
    facebook = models.URLField(null=True, blank=True)
    twitter = models.URLField(null=True, blank=True)
    instagram = models.URLField(null=True, blank=True)
    youtube = models.URLField(null=True, blank=True)
    site = models.OneToOneField(
        to=Site, on_delete=models.CASCADE, related_name='site_social'
    )

    class Meta:
        db_table = "social_settings"
        verbose_name = _("Social Settings")
        verbose_name_plural = _("Social Settings")

    def __str__(self):
        return "Social Settings"


class AuthenticationSettings(BaseModel):
    updated_at = None
    created_at = None
    activation_days = models.PositiveSmallIntegerField(default=7)
    registration_auto_login = models.BooleanField(default=False)
    send_activation_email = models.BooleanField(default=True)
    registration_open = models.BooleanField(default=True)
    site = models.OneToOneField(
        to=Site, on_delete=models.CASCADE, related_name='site_auth'
    )

    def __str__(self):
        return "Authentication Settings"

    class Meta:
        db_table = "auth_settings"
        verbose_name = _("Authentication Settings")
        verbose_name_plural = _("Authentication Settings")
