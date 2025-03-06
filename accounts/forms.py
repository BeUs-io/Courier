from django import forms
from django.contrib.auth.forms import (
    PasswordChangeForm as DjangoPasswordChangeForm,
    PasswordResetForm as DjangoPasswordResetForm
)
from django.core.mail import EmailMessage
from django.template import loader
from registration import forms as reg
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from crispy_forms import layout, helper
from django.contrib.auth.password_validation import validate_password
from core.utils.utils import get_form_button
from . import models
from dashboard import forms as dash_forms
from django.contrib.auth.models import Permission
from django.conf import settings


# PERMISSION MODEL EXCLUDE
APP_LIST_EXCLUDE = [
    'auth', 'sites', "admin", "contenttypes", "registration", "sessions"
]
CODENAME_EXCLUDE = [
    "add_socialsetting", "delete_socialsetting", "add_sitesettings",
    "delete_sitesettings", "add_authenticationsettings",
    "delete_authenticationsettings"
]

MODEL_LIST_EXCLUDE = ["userlogs"]


class RegistrationForm(reg.RegistrationForm):
    email = forms.EmailField(label="Email")
    password1 = forms.CharField(
        label=_("Password"), strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"})
    )
    password2 = forms.CharField(
        label=_("Password confirmation"), strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"})
    )

    class Meta:
        model = get_user_model()
        fields = ("name", "email", "password1", "password2", "agree")
        widgets = {"name": forms.TextInput(attrs={"autofocus": True})}

    def clean(self):
        super().clean()

        if not self.cleaned_data['agree']:
            self.add_error('agree', _("This field is required."))


class AccountProfileModelForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['name', 'phone', 'address', 'designation', 'avatar']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = helper.FormHelper()
        self.helper.layout = layout.Layout(
            layout.Row(
                layout.Column('name', css_class='form-group col-md-6 mb-0'),
                layout.Column('phone', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'address',
            layout.Row(
                layout.Column(
                    'designation', css_class='form-group col-md-6 mb-0'
                ),
                layout.Column('avatar', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            layout.Column(
                layout.Submit('submit', "Update", css_class="px-4"),
                css_class='text-end'
            ),
        )


class AccountDeleteForm(forms.Form):
    password = forms.CharField(
        widget=forms.TextInput(attrs={'type': "password"})
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.helper = helper.FormHelper()
        self.helper.layout = layout.Layout(
            'password',
            layout.Column(
                layout.Submit(
                    'submit', "Delete account", css_class="px-4 btn-danger"
                ),
                css_class='text-end'
            ),
        )

    def clean(self):
        if not self.user.check_password(self.cleaned_data['password']):
            self.add_error(
                'password', "Your old password was entered incorrectly."
            )


class PasswordChangeForm(DjangoPasswordChangeForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False, label=_("New password"),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = helper.FormHelper()
        self.helper.layout = layout.Layout(
            'old_password',
            layout.Row(
                layout.Column(
                    'new_password1',
                    css_class='form-group col-md-6 mb-0'
                ),
                layout.Column(
                    'new_password2',
                    css_class='form-group col-md-6 mb-0'
                ),
                css_class='form-row'
            ),
            layout.Column(
                layout.Submit(
                    'submit', "Change password", css_class="px-4"
                ),
                css_class='text-end'
            ),
        )


class UserGroupModelForm(forms.ModelForm):
    class Meta:
        model = models.Group
        fields = ['name', 'permissions']
        widgets = {
            'permissions': forms.SelectMultiple(
                attrs={'class': 'multiSelect2', 'multiple': 'multiple'}
            ),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.helper = helper.FormHelper()
        button_title = "Save"
        delete = ""
        self.fields['permissions'].queryset = Permission.objects.select_related().exclude(  # noqa
            content_type__app_label__in=APP_LIST_EXCLUDE).\
            exclude(codename__in=CODENAME_EXCLUDE).\
            exclude(content_type__model__in=MODEL_LIST_EXCLUDE)
        if self.instance.name:
            button_title = "Update"
            delete = self.instance
        self.helper.layout = layout.Layout(
            "name",
            "permissions",
            get_form_button(
                button_title, delete, user=self.user,
                model="group", app="accounts"
            )
        )


class UserModelForm(forms.ModelForm):
    password = forms.CharField(
        required=False, validators=[validate_password],
        widget=forms.PasswordInput(attrs={'type': "password"})
    )
    password2 = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'type': "password"})
    )

    class Meta:
        model = get_user_model()
        fields = [
            'name', 'phone', 'address', 'designation', 'avatar', 'email',
            'password', 'password2', 'groups', "groups", "user_permissions",
            "is_staff", 'is_active', 'is_superuser'
        ]
        widgets = {
            'groups': forms.SelectMultiple(
                attrs={'class': 'multiSelect2', 'multiple': 'multiple'}
            ),
            'user_permissions': forms.SelectMultiple(
                attrs={'class': 'multiSelect2', 'multiple': 'multiple'}
            ),
        }
        labels = {
            "user_permissions": "Permissions"
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        button_title = "Save"
        delete = ""

        password_change = ""
        self.fields['user_permissions'].queryset = Permission.objects.\
            select_related().exclude(
            content_type__app_label__in=APP_LIST_EXCLUDE).exclude(
                codename__in=CODENAME_EXCLUDE
        ).exclude(content_type__model__in=MODEL_LIST_EXCLUDE)

        if self.instance.name:
            button_title = "Update"
            self.fields['password2'].initial = self.instance.password
            url = self.instance.get_pass_update_url()
            password_change = f"""<div class='mb-1'><small>Raw passwords are not stored, so there is no way to see
             this user’s password, but you can change the password using <a href='{url}'>this form</a>.</small></div>"""  # noqa
            delete = self.instance
        self.helper = helper.FormHelper()

        self.helper.layout = layout.Layout(
            layout.Row(
                layout.Column('name', css_class='form-group col-md-6 mb-0'),
                layout.Column('email', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            layout.Row(
                layout.Column('phone', css_class='form-group col-md-6 mb-0'),
                layout.Column('address', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            layout.Row(
                layout.Column('designation', css_class='form-group col-md-6 mb-0'),  # noqa
                layout.Column('avatar', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'user_permissions',
            layout.Row(
                layout.Column('password', css_class='form-group col-md-6 mb-0'),  # noqa
                layout.Column('password2', css_class='form-group col-md-6 mb-0'),  # noqa
                css_class='form-row'
            ),
            layout.Row(
                layout.Column('is_staff', css_class='my-auto form-group col-md-6'),  # noqa
                layout.Column('groups', css_class='form-group col-md-6 mb-0'),  # noqa
                css_class='form-row'
            ),
            layout.Row(
                layout.Column('is_active', css_class='form-group col-md-6 mb-0'),  # noqa
                layout.Column('is_superuser', css_class='form-group col-md-6 mb-0'),  # noqa
                css_class='form-row'
            ),
            layout.HTML(password_change),
            get_form_button(
                button_title, delete, user=self.user, model="users",
                app="accounts"
            )
        )
        if self.instance.name:
            self.fields['password'] = forms.CharField(
                widget=forms.TextInput(attrs={"type": "hidden"})
            )
            self.fields['password2'] = forms.CharField(
                widget=forms.TextInput(attrs={"type": "hidden"})
            )


class UserPasswordUpdateForm(forms.Form):
    email = forms.EmailField(disabled=True)
    password = forms.CharField(
        required=False,
        validators=[validate_password],
        initial=""
    )
    password2 = forms.CharField(
        required=False,
        initial=""
    )

    def clean(self):
        if self.cleaned_data['password'] != self.cleaned_data['password2']:
            self.add_error('password', 'password not matched')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = helper.FormHelper()
        self.helper.layout = layout.Layout(
            'email',
            layout.Row(
                layout.Column('password', css_class='form-group col-md-6 mb-0'),  # noqa
                layout.Column('password2', css_class='form-group col-md-6 mb-0'),  # noqa
                css_class='form-row'
            ),
            layout.Column(
                layout.Submit('submit', "Update", css_class="px-4"),
                css_class='text-end'
            ),
        )


class DesignationModelForm(dash_forms.CategoryModelForm):
    model_name = "designationmodel"
    app_name = "accounts"

    class Meta:
        model = models.DesignationModel
        fields = ['title', 'description', 'is_active']
        widgets = {'description': forms.Textarea(attrs={'rows': 1})}


class PasswordResetForm(DjangoPasswordResetForm):
    def send_mail(
        self, subject_template_name, email_template_name, context, from_email,
        to_email, html_email_template_name=None
    ):
        self.custom_mail(subject_template_name, email_template_name, context,
                         from_email, to_email, html_email_template_name
                         )

    @staticmethod
    def custom_mail(
        subject_template_name, email_template_name, context, from_email,
        to_email, html_email_template_name
    ):
        from configuration.models import SiteSettings
        ams = SiteSettings.objects.filter(site__id=settings.SITE_ID).first()
        context.update(
            {"ams": ams, "admin_email": settings.DEFAULT_FROM_EMAIL})
        subject = f"Password reset on {context.get('site_name')}"
        message = loader.get_template(email_template_name).render(context)
        mail = EmailMessage(
            subject=subject, body=message, from_email=from_email,
            to=[to_email], reply_to=[from_email]
        )
        mail.content_subtype = "html"
        return mail.send()


class UserInviteModelForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = (
            'name', 'email', 'designation', 'is_active', 'is_staff',
            'is_superuser', 'groups', 'user_permissions'
        )
        widgets = {
            'groups': forms.SelectMultiple(
                attrs={'class': 'multiSelect2', 'multiple': 'multiple'}
            ),
            'user_permissions': forms.SelectMultiple(
                attrs={'class': 'multiSelect2', 'multiple': 'multiple'}
            ),
        }
        labels = {
            "user_permissions": "Permissions"
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user_permissions'].queryset = Permission.objects.\
            select_related().exclude(
            content_type__app_label__in=APP_LIST_EXCLUDE).exclude(
                codename__in=CODENAME_EXCLUDE
        ).exclude(content_type__model__in=MODEL_LIST_EXCLUDE)
        self.helper = helper.FormHelper()
        self.helper.layout = layout.Layout(
            layout.Row(
                layout.Column('name', css_class='form-group col-md-6 mb-0'),
                layout.Column('email', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'user_permissions',
            layout.Row(
                layout.Column('is_staff', css_class='my-auto order-2 order-md-1 form-group col-md-6'),  # noqa
                layout.Column('groups', css_class='form-group order-1 order-md-2 col-md-6 mb-0'),  # noqa
                css_class='form-row'
            ),
            layout.Row(
                layout.Column('is_active', css_class='form-group col-md-6'),
                layout.Column('is_superuser', css_class='form-group col-md-6 mb-0'),  # noqa
                css_class='form-row'
            ),
            layout.Column(
                layout.Submit('submit', "Invite", css_class="px-4"),
                css_class='text-end'
            ),
        )


class UserInviteSetPassword(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput,
        label="New password",
        validators=[validate_password]
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput,
        label="New password confirmation",
    )

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password") != cleaned_data.get("password2"):
            self.add_error("password2", "Password fields didn’t match.")
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = helper.FormHelper()
        self.helper.layout = layout.Layout(
            'password',
            'password2',
            layout.Column(
                layout.Submit('submit', "Set Password", css_class="px-4"),
                css_class='text-end'
            ),
        )
