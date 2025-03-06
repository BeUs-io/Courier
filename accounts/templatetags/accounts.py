import logging
from django import template
from core.utils.decorator import _check_perms
from django.apps import apps
register = template.Library()


@register.filter
def perms_require(request, perm):
    return _check_perms(request.user, perm)


@register.filter
def get_model_name(_object):
    try:
        model = apps.get_model(
            app_label=_object.content_type.app_label,
            model_name=_object.content_type.model
        )
        return model._meta.verbose_name
    except Exception as e:
        logging.error(e)
        return "Unknown"
