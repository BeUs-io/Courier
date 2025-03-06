import logging
import uuid
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models
from accounts.managers import UserManager
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext as _
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group as DjangoGroup
from django.urls import reverse_lazy
from core.base.model import BaseModel
from django.utils import timezone
from django.shortcuts import get_object_or_404


ADDITION = 1
CHANGE = 2
DELETION = 3


class Group(DjangoGroup):
    class Meta:
        proxy = True
        permissions = [("export_group", "Can Export Groups")]

    def __str__(self) -> str:
        if self.name:
            return self.name
        return "Unknown"

    def get_absolute_url(self):
        return reverse_lazy("user_groups_update", kwargs={"pk": self.pk})

    def get_absolute_delete_url(self):
        return reverse_lazy("user_groups_delete", kwargs={"pk": self.pk})

    @staticmethod
    def add_another_url():
        return reverse_lazy("user_groups_form")

    @staticmethod
    def list_url():
        return reverse_lazy("user_groups_list")


class DesignationModel(BaseModel):
    title = models.CharField(
        max_length=50, verbose_name=_("Title"), unique=True
    )
    description = models.TextField(
        null=True, blank=True, verbose_name=_("Description")
    )
    is_active = models.BooleanField(
        default=True, verbose_name=_("Active")
    )

    def get_absolute_url(self):
        return reverse_lazy("designation_update", kwargs={"pk": self.pk})

    def get_absolute_delete_url(self):
        return reverse_lazy("designation_delete", kwargs={"pk": self.pk})

    @staticmethod
    def add_another_url():
        return reverse_lazy("designation_form")

    @staticmethod
    def list_url():
        return reverse_lazy("designation_list")

    class Meta:
        db_table = 'designation'
        verbose_name = _("Designation")
        verbose_name_plural = _("Designations")
        permissions = [("export_designation", "Can Export Designations")]

    def __str__(self) -> str:
        if self.title:
            return self.title
        return "Unknown"


# Create your models here.
class Users(AbstractUser, BaseModel):
    updated_at = created_at = first_name = last_name = username = None
    name = models.CharField(_("Name"), max_length=150, null=True)
    email = models.EmailField(_("Email"), unique=True)
    avatar = models.ImageField(
        upload_to='users/avatar/', null=True, blank=True
    )
    phone = models.CharField(max_length=30, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    extra_detail = models.TextField(null=True, blank=True)
    designation = models.ForeignKey(
        to=DesignationModel, on_delete=models.SET_NULL, null=True, blank=True
    )
    agree = models.BooleanField(
        default=True, verbose_name=_("I read and agree to terms & conditions")
    )
    objects = UserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['name']

    def get_pass_update_url(self):
        return reverse_lazy("user_pass_update", kwargs={"pk": self.pk})

    def get_absolute_url(self):
        return reverse_lazy("user_update", kwargs={"pk": self.pk})

    def get_absolute_delete_url(self):
        return reverse_lazy("user_delete", kwargs={"pk": self.pk})

    @staticmethod
    def add_another_url():
        return reverse_lazy("user_create")

    @staticmethod
    def list_url():
        return reverse_lazy("user_list")

    def role(self):
        if self.is_superuser:
            return "Admin"
        elif self.is_staff:
            return "Staff"
        else:
            return "Active User"

    def bade_role(self):
        if self.is_superuser:
            return "badge bg-primary rounded-pill"
        elif self.is_staff:
            return "badge bg-info rounded-pill"
        else:
            return "badge bg-dark rounded-pill"

    @staticmethod
    def get_employee(active=False):
        return get_user_model().objects.filter(
            is_employee=True, is_active=active
        )

    @staticmethod
    def get_users(active=False):
        return get_user_model().objects.filter(
            is_employee=False, avatar=active
        )

    def __str__(self) -> str:
        if self.get_full_name():
            return self.get_full_name()
        return "Unknown"

    @staticmethod
    def get_avatar_svg(_class):
        return f"""
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="text-primary {_class} bi bi-person-circle" viewBox="0 0 16 16">
              <path d="M11 6a3 3 0 1 1-6 0 3 3 0 0 1 6 0z"/>
              <path fill-rule="evenodd" d="M0 8a8 8 0 1 1 16 0A8 8 0 0 1 0 8zm8-7a7 7 0 0 0-5.468 11.37C3.242 11.226 4.805 10 8 10s4.757 1.225 5.468 2.37A7 7 0 0 0 8 1z"/>
            </svg>"""  # noqa

    def get_avatar_10(self):
        if self.avatar:
            return f"""<img class="rounded-circle w-10 h-10 ms-2" src="{self.avatar.url}">"""  # noqa
        return self.get_avatar_svg("h-8 w-8")

    def get_avatar_16(self):
        if self.avatar:
            return f"""<img class="rounded-circle w-16 h-16 ms-2 ms-0" src="{self.avatar.url}">"""  # noqa
        return self.get_avatar_svg("h-16 w-16")

    def get_full_name(self):
        if self.name:
            return self.name
        return "Unknown"

    class Meta(AbstractUser.Meta):
        db_table = 'users'
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        permissions = [("export_users", "Can Export Users")]


class UserLogs(BaseModel):
    updated_at = None
    created_at = None
    ACTION_FLAG_CHOICES = (
        (ADDITION, _("Addition")),
        (CHANGE, _("Change")),
        (DELETION, _("Deletion")),
    )
    user = models.ForeignKey(
        to=get_user_model(), on_delete=models.CASCADE, verbose_name=_("User")
    )
    content_type = models.ForeignKey(
        ContentType, models.SET_NULL, verbose_name=_("content type"),
        blank=True, null=True
    )
    object_id = models.TextField(_("object id"), blank=True, null=True)
    action = models.PositiveSmallIntegerField(
        _("action flag"), choices=ACTION_FLAG_CHOICES
    )
    message = models.TextField(_("change message"), blank=True)
    action_time = models.DateTimeField(
        _("action time"), auto_now_add=True, editable=False
    )

    def __str__(self):
        return self.user.get_full_name()

    class Meta:
        permissions = [("export_login_logs", "Can Export Login Logs")]
        verbose_name = _("user log entry")
        verbose_name_plural = _("user log entries")
        db_table = "user_log"
        ordering = ["-action_time"]

    def get_action_html(self):
        if ADDITION == self.action:
            return "<span class='text-success'>Add</span>"
        elif CHANGE == self.action:
            return "<span class='text-warning'>Change</span>"
        elif DELETION == self.action:
            return "<span class='text-danger'>Delete</span>"

    @classmethod
    def get_action(cls, action, _change_data, _obj, verbose_name):
        __str__ = getattr(_obj, "__str__")
        if __str__:
            _str = __str__()
        else:
            _str = "Unknown"

        if ADDITION == action:
            return f"{_str}"
        elif CHANGE == action:
            change_filed = ", ".join(_change_data)
            return f"[{change_filed}] on {_str}"
        elif DELETION == action:
            return f"{__str__()}"

    @classmethod
    def create_log(cls, request, _obj, _action, changed_data=None):
        if settings.USER_LOGS:
            try:
                app_label = _obj._meta.app_label
                model = _obj._meta.model_name
                verbose_name = _obj._meta.verbose_name
                content_type = ContentType.objects.get(
                    app_label=app_label, model=model
                )
                message = cls.get_action(
                    _action, changed_data, _obj, verbose_name
                )
                user_log = UserLogs.objects.create(
                    user=request.user, content_type=content_type,
                    action=_action, message=message
                )
                if not _action == DELETION:
                    user_log.object_id = _obj.pk
                    user_log.save()
                if not changed_data and _action == CHANGE:
                    user_log.delete()
            except Exception as e:
                logging.error(e)


class UserToken(models.Model):
    class TokenType(models.IntegerChoices):
        INVITE = 1, _("Invite")

    user = models.OneToOneField(
        get_user_model(), on_delete=models.CASCADE, related_name="token"
    )
    token = models.CharField(max_length=100)
    type = models.PositiveSmallIntegerField(choices=TokenType.choices)
    expires = models.DateTimeField()

    @classmethod
    def expires_date(cls):
        return timezone.now() + timezone.timedelta(days=7)

    @classmethod
    def make_token(cls, user, type):
        token = uuid.uuid4().hex
        if not cls.objects.filter(user=user, token=token).exists():
            user_token = cls.objects.create(
                user=user, token=token, type=type,
                expires=cls.expires_date()
            )
            print(user_token)
            return token, user_token
        return cls.make_token(user, type)

    @classmethod
    def check_token(cls, token, type):
        return get_object_or_404(
            UserToken, token=token, type=type, expires__gte=timezone.now()
        )
