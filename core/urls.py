from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView, TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include('dashboard.urls')),
    path('', include('assetdash.urls')),
    path('', RedirectView.as_view(url="dashboard/")),
    path('account/', include('accounts.urls')),
    path('settings/', include('configuration.urls')),
    path('account/', include('registration.backends.default.urls')),
    path(
        "under-construction/",
        TemplateView.as_view(
            template_name='configuration/under_construction.html'
        ),
        name="construction"
    )
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns.append(path('__debug__/', include('debug_toolbar.urls')))

handler400 = 'core.utils.handler.custom_bad_request_view'
handler403 = 'core.utils.handler.custom_permission_denied_view'
handler404 = 'core.utils.handler.custom_page_not_found_view'
handler500 = 'core.utils.handler.custom_error_view'
