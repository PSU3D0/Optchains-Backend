from django.conf import settings
from django.core.management import execute_from_command_line
import os
import sys
import logging



settings.configure(
    DEBUG=False,
    DATABASES = {
        "default": {
            "ENGINE": os.environ.get("SQL_ENGINE"),
            "NAME": os.environ.get("SQL_DATABASE"),
            "USER": os.environ.get("SQL_USER", "user"),
            "PASSWORD": os.environ.get("SQL_PASSWORD", "password"),
            "HOST": os.environ.get("SQL_HOST", "localhost"),
            "PORT": os.environ.get("SQL_PORT", "5432"),
        }
    },
    ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS","127.0.0.1").split(" "),
    INSTALLED_APPS = (
        'database',
        'updater.apps.UpdaterConfig'
    ),
    USE_TZ=True,
    TIME_ZONE = 'UTC',
    API_PROVIDER = 'yfinance',
)

execute_from_command_line(sys.argv)