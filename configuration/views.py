from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import generic
from core.middlewares import auth_config
from core.utils.decorator import perms_require, CHANGE, VIEW
from . import forms, models
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
from accounts import models as ac_models
from accounts.decorators import login_required


@method_decorator([login_required(staff=True), perms_require(f"configuration.{VIEW}sitesettings")], name="dispatch")  # noqa
class SiteSettingsUpdateView(generic.UpdateView):
    model = models.SiteSettings
    template_name = "configuration/site_settings_form.html"
    form_class = forms.SiteSettingsModelForm
    extra_context = {
        "segment": "settings", 'sub_segment': "site",
        "title": "Site Settings"
    }
    success_url = reverse_lazy('site_settings')

    def dispatch(self, request, *args, **kwargs):
        current_site = get_current_site(self.request)
        if not hasattr(current_site, 'site_general'):
            self.model.objects.create(site=current_site)
        self.site_general = getattr(current_site, 'site_general')
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self.site_general

    @method_decorator(perms_require(f"configuration.{CHANGE}sitesettings"))
    def form_valid(self, form):
        form_obj = form.save()
        title = form.cleaned_data['display_name']
        form_obj.site.name = title
        form_obj.site.domain = form.cleaned_data['domain_name']
        form_obj.site.save()
        ac_models.UserLogs.create_log(
            self.request, form_obj, ac_models.CHANGE,
            changed_data=form.changed_data
        )
        messages.success(self.request, f"{title} was updated successfully!")
        return redirect(self.success_url)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        site = self.get_object().site
        kwargs['display_name'] = site.name
        kwargs['domain_name'] = site.domain
        return kwargs


@method_decorator([login_required(staff=True), perms_require(f"configuration.{VIEW}socialsetting")], name="dispatch")  # noqa
class SocialSettingsUpdateView(generic.UpdateView):
    model = models.SocialSetting
    template_name = "configuration/social_settings_form.html"
    form_class = forms.SocialSettingModelForm
    extra_context = {
        "segment": "settings", 'sub_segment': "social", 'title': "Social"
    }
    success_url = reverse_lazy('social_settings')

    def dispatch(self, request, *args, **kwargs):
        current_site = get_current_site(self.request)
        if not hasattr(current_site, 'site_social'):
            self.model.objects.create(site=current_site)
        self.site_social = getattr(current_site, 'site_social')
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self.site_social

    @method_decorator(perms_require(f"configuration.{CHANGE}socialsetting"))
    def form_valid(self, form):
        form_obj = form.save()
        messages.success(
            self.request, "Social settings was updated successfully!"
        )
        ac_models.UserLogs.create_log(
            self.request, form_obj, ac_models.CHANGE,
            changed_data=form.changed_data
        )
        return redirect(self.success_url)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


@method_decorator([
    login_required(staff=True),
    perms_require(f"configuration.{VIEW}authenticationsettings")
    ], name="dispatch")
class AuthSettingsUpdateView(generic.UpdateView):
    model = models.AuthenticationSettings
    template_name = "configuration/auth_settings_form.html"
    form_class = forms.AuthSettingModelForm
    extra_context = {
        "segment": "settings", 'sub_segment': "auth",
        'title': "Authentication"
    }
    success_url = reverse_lazy('auth_settings')

    def dispatch(self, request, *args, **kwargs):
        current_site = get_current_site(self.request)
        if not hasattr(current_site, 'site_auth'):
            self.model.objects.create(site=current_site)
        self.site_auth = getattr(current_site, 'site_auth')
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self.site_auth

    @method_decorator(perms_require(f"configuration.{CHANGE}authenticationsettings"))  # noqa
    def form_valid(self, form):
        form_obj = form.save()
        messages.success(
            self.request,
            "Authentication settings was updated successfully!"
        )
        ac_models.UserLogs.create_log(
            self.request, form_obj, ac_models.CHANGE,
            changed_data=form.changed_data
        )
        auth_config(get_current_site(self.request))
        return redirect(self.success_url)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs
