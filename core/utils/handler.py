from django.shortcuts import render


def custom_page_not_found_view(request, exception):
    context = {
        'title': "Error 404 – Page Not Found",
        'status_code': 404,
        'message': "The page you requested was not found."
    }
    return render(request, "error.html", context)


def custom_error_view(request, exception=None):
    context = {
        'title': "Error 500 – Server Error",
        'status_code': 500,
        'message': "Oops, something went wrong."
    }
    return render(request, "error.html", context)


def custom_permission_denied_view(request, exception=None):
    context = {
        'title': "Error 403 – Forbidden",
        'status_code': 403,
        'message': "You don’t have permission to access this url on this server."  # noqa
        }
    return render(request, "error.html", context)


def custom_bad_request_view(request, exception=None):
    context = {
        'title': "Error 400 – Bad Request",
        'status_code': 400,
        'message': "You've sent a bad request."
    }
    return render(request, "error.html", context)
