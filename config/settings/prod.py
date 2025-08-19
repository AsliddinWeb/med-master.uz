from .base import *
from decouple import config

# ALLOWED_HOSTS = ['med-master.uz', 'www.med-master.uz', '164.92.240.184', 'localhost']

# Database (production uchun PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config('DB_NAME', default='db_name'),
        'USER': config('DB_USER', default='db_user'),
        'PASSWORD': config('DB_PASSWORD', default='db_password'),
        'HOST': 'localhost',
        'PORT': '',
    }
}

# # Security sozlamalari
# SECURE_SSL_REDIRECT = True
# SECURE_BROWSER_XSS_FILTER = True
# SECURE_CONTENT_TYPE_NOSNIFF = True