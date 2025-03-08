import uuid
from django.db import models
from django.utils.translation import gettext as _


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name=_("Updated At")
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Created At")
    )

    class Meta:
        abstract = True
