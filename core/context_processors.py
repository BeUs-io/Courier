from django.contrib.sites.shortcuts import get_current_site
from configuration.models import SocialSetting, SiteSettings


def ams_context_processor(request):
    _site = get_current_site(request)
    site_social, _ = SocialSetting.objects.get_or_create(site=_site)
    ams, _ = SiteSettings.objects.get_or_create(site=_site)
    context = {"ams": ams, "site_social": site_social, "site": _site}
    return context
