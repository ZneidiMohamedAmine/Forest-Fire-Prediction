import os
from django.core.exceptions import ImproperlyConfigured

DJANGO_ENV = os.environ.get('DJANGO_ENV', 'development')

if DJANGO_ENV == 'production':
    from .production import *
elif DJANGO_ENV == 'staging':
    from .staging import *
elif DJANGO_ENV in ('development', 'docker'):
    from .development import *
else:
    raise ImproperlyConfigured(
        f"DJANGO_ENV '{DJANGO_ENV}' is invalid. "
        f"Must be one of: development, staging, production, docker"
    )
