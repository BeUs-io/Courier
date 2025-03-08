import pytz
import logging
from django.conf import settings
from django.utils import timezone
from crispy_forms import layout
from core.utils.decorator import _check_perms, ADD, DELETE

ADD_ANOTHER = "add_another"
CONTINUE_URL = "continue_url"
ADD_ANOTHER_TITLE = "Save and add another"
CONTINUE_URL_TITLE = "Save and continue editing"
timezone_pytz = [[tz, tz] for tz in pytz.common_timezones]


def get_timezone():
    return timezone.datetime.now(timezone.get_current_timezone())


arm_timezone = get_timezone()


def get_current_timezone():
    return timezone.get_current_timezone()


def convert_current_timezone(date):
    try:
        return date.astimezone(
            pytz.timezone(
                str(get_current_timezone()) or settings.TIME_ZONE
            )
        )
    except Exception as e:
        logging.error(e)
        return date


def get_user_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')


def redirect_to_another_url(request, obj):
    if request.POST.get(ADD_ANOTHER):
        return obj.add_another_url()
    elif request.POST.get(CONTINUE_URL):
        return obj.get_absolute_url()
    return obj.list_url()


def get_form_button(button_title, can_delete, user, app, model):
    if can_delete and _check_perms(user, f"{app}.{DELETE}{model}"):
        can_delete = can_delete.get_absolute_delete_url()
        delete_btn = f"<a href='{can_delete}' class='DeleteBTN btn mt-1 mx-1 btn-danger'>Delete</a>"  # noqa
    else:
        delete_btn = ""
    add_button = ""
    if _check_perms(user, f"{app}.{ADD}{model}"):
        add_button = f"""
            <div class="order-1 order-sm-3 col-sm-auto col-6 m-1"><input type="submit"
             class="btn btn-primary" value="{button_title}" name="submit"></div>
            <div class="order-3 order-sm-1 col-sm-auto col-6 m-1"><input type="submit"
            class="btn btn-primary" value="{ADD_ANOTHER_TITLE}" name="{ADD_ANOTHER}"></div>
            <div class="order-2 order-sm-2 col-sm-auto col-6 m-1"><input type="submit"
            class="btn btn-primary" value="{CONTINUE_URL_TITLE}" name="{CONTINUE_URL}"></div>
        """  # noqa
    return layout.Row(
        layout.Column(
            layout.HTML(delete_btn),
            css_class='col-auto order-sm-1 order-2 order-md-2'
        ),
        layout.Column(
            layout.HTML(add_button),
            css_class="row col-auto order-sm-2 order-1 order-md-2"
        ),
        css_class="justify-content-between"
    )


def get_domain(request, extra='') -> str:
    return f"{request.scheme}://{request.get_host()}{extra}"
