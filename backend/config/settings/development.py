"""
Development settings for TIME BLOCK project.
"""

from .base import *

# Debug mode
DEBUG = True

# Allowed hosts
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '192.168.56.1']

# CORS - allow all origins in development
CORS_ALLOW_ALL_ORIGINS = True

# Database - use local PostgreSQL
# Inherits from base.py, can be overridden via .env

# Logging - more verbose in development
LOGGING['root']['level'] = 'DEBUG'
LOGGING['loggers']['django']['level'] = 'DEBUG'

# Django Debug Toolbar (optional - uncomment to use)
# INSTALLED_APPS += ['debug_toolbar']
# MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
# INTERNAL_IPS = ['127.0.0.1']

# Email backend - console in development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
