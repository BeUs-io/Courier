from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission


admin.site.register(get_user_model())
admin.site.register(Permission)
