from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test

VIEW = "view_"
CHANGE = "change_"
DELETE = "delete_"
ADD = "add_"


def perms_require(perm, login_url=None, raise_exception=True):
    def check_perms(user):
        if isinstance(perm, str):
            perms = (perm,)
        else:
            perms = perm
        if user.has_perms(perms):
            return True
        if raise_exception:
            raise PermissionDenied
        return False
    return user_passes_test(check_perms, login_url=login_url)


def _check_perms(user, perm):
    if user.has_perms([perm]):
        return True
    return False
