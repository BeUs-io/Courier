from django import forms
from django.contrib.sites.models import _simple_domain_name_validator
from core.utils.decorator import _check_perms, CHANGE
from . import models
from crispy_forms import layout, helper


def get_button_update(user, perm):
    if _check_perms(user, perm):
        return layout.Column(
            layout.Submit('submit', "Update", css_class="px-4"),
            css_class='text-end'
        )
    return layout.Column(layout.HTML(""))


class SiteSettingsModelForm(forms.ModelForm):
    display_name = forms.CharField(label="Site Name")
    domain_name = forms.CharField(validators=[_simple_domain_name_validator])
    color = forms.CharField(
        label="Theme Color",
        widget=forms.TextInput(
            attrs={"type": "color", "oninput": "colorChange()"}
        )
    )

    class Meta:
        model = models.SiteSettings
        fields = [
            'logo', 'favicon', 'timezone', 'color', 'display_name', "user_bar",
            'domain_name', "under_construction", "message", "user_logs"
        ]
        widgets = {"message": forms.Textarea(attrs={'rows': 3})}

    def clean(self):
        if self.cleaned_data['under_construction']:
            if not self.cleaned_data['message']:
                self.add_error(
                    "message", "Please write under construction message."
                )

    def __init__(self, user, display_name, domain_name, *args, **kwargs):
        self.user = user
        self._display_name = display_name
        self._domain_name = domain_name
        super().__init__(*args, **kwargs)
        self.helper = helper.FormHelper()
        self.fields['display_name'].initial = display_name
        self.fields['domain_name'].initial = domain_name
        self.helper.layout = layout.Layout(
            layout.Row(
                layout.Column(
                    'display_name', css_class='form-group col-md-6 mb-0'
                ),
                layout.Column(
                    'domain_name', css_class='form-group col-md-6 mb-0'
                ),
                css_class='form-row'
            ),
            layout.Row(
                layout.Column('color', css_class='form-group col-md-6 mb-0'),
                layout.Column(
                    'timezone', css_class='form-group col-md-6 mb-0'
                ),
                css_class='form-row'
            ),
            layout.Row(
                layout.Column('logo', css_class='form-group col-md-6 mb-0'),
                layout.Column('favicon', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            layout.Row(
                layout.Column(
                    'user_bar', css_class='form-group col-md-6 mb-0'
                ),
                layout.Column(
                    'user_logs', css_class='form-group col-md-6 mb-0'
                ),
                css_class='form-row'
            ),
            "under_construction",
            'message',
            get_button_update(
                user=user, perm=f"configuration.{CHANGE}sitesettings"
            )
        )


class SocialSettingModelForm(forms.ModelForm):
    class Meta:
        model = models.SocialSetting
        fields = ('facebook', 'twitter', 'instagram', 'youtube')

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.helper = helper.FormHelper()
        self.helper.layout = layout.Layout(
            layout.Row(
                layout.Column(
                    'facebook', css_class='form-group col-md-6 mb-0'
                ),
                layout.Column(
                    'twitter', css_class='form-group col-md-6 mb-0'
                ),
                css_class='form-row'
            ),
            layout.Row(
                layout.Column(
                    'instagram', css_class='form-group col-md-6 mb-0'
                ),
                layout.Column(
                    'youtube', css_class='form-group col-md-6 mb-0'
                ),
                css_class='form-row'
            ),
            get_button_update(
                user=user,
                perm=f"configuration.{CHANGE}socialsetting"
            )
        )


class AuthSettingModelForm(forms.ModelForm):
    class Meta:
        model = models.AuthenticationSettings
        fields = (
            'activation_days', 'registration_auto_login',
            'send_activation_email', 'registration_open'
        )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.helper = helper.FormHelper()
        self.helper.layout = layout.Layout(
            layout.Row(
                layout.Column(
                    'activation_days',
                    css_class='form-group col-md-6 col-lg-4 mb-0'
                ),
                layout.Column(
                    'registration_auto_login',
                    css_class='form-group col-lg-4 col-md-6 pt-md-4 mt-md-3 mb-0'  # noqa
                ),
                layout.Column(
                    'send_activation_email',
                    css_class='form-group col-lg-4 col-md-6 pt-md-4 mt-lg-3 mb-0'  # noqa
                ),
                layout.Column(
                    'registration_open',
                    css_class='form-group col-lg-4 col-md-6 pt-md-4 mb-0'
                ),
                css_class='form-row'
            ),
            get_button_update(
                user=user, perm=f"configuration.{CHANGE}authenticationsettings"
            )
        )
