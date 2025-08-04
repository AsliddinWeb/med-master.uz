import os

# Environment variable orqali settings tanlash
environment = os.environ.get('DJANGO_ENV', 'dev')

if environment == 'prod':
    from .prod import *
else:
    from .dev import *