from django.db.models.signals import post_save
from django.dispatch import receiver
from . import models


@receiver(post_save, sender=models.Site)
def create_object_link_site(sender, created, instance, **kwargs):
    if created:
        models.SiteSettings.objects.create(site=instance)
        models.SocialSetting.objects.create(site=instance)
        models.AuthenticationSettings.objects.create(site=instance)
