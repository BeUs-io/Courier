from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.shortcuts import redirect
from django.conf import settings


def login_required(
    staff=False,
    redirect_field_name=REDIRECT_FIELD_NAME,
    login_url=settings.LOGIN_URL
):
    user_pass = user_passes_test(
        lambda u: u.is_authenticated and u.is_active,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if staff:
        def decorator(view_func):
            @user_pass
            def _wrapped_view(request, *args, **kwargs):
                if request.user.is_staff or request.user.is_superuser:
                    return view_func(request, *args, **kwargs)
                else:
                    return redirect('assetdash')
            return _wrapped_view
        return decorator
    else:
        return user_pass
