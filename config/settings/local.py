# config/settings/local.py
from .base import * 

DEBUG = True
SECRET_KEY = 'django-insecure-dev-key'
ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1"]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}