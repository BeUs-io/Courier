from django.urls import path
from . import views

urlpatterns = [
    path('', views.SiteSettingsUpdateView.as_view(), name="site_settings"),
    path(
        'social-settings/',
        views.SocialSettingsUpdateView.as_view(),
        name="social_settings"
    ),
    path(
        'auth-settings/',
        views.AuthSettingsUpdateView.as_view(),
        name="auth_settings"
    ),
]
