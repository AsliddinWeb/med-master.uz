from .base import *

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Database (development uchun SQLite)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
