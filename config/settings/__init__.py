from decouple import config

# Environment variable orqali settings tanlash
environment = config('DJANGO_ENV', default='dev')

if environment == 'prod':
    from .prod import *
else:
    from .dev import *