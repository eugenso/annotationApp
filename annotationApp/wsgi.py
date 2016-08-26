"""
WSGI config for annotationApp project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os

# os.environ['DJANGO_SETTINGS_MODULE'] = 'annotationApp.settings'

# from django.contrib.auth.handlers.modwsgi import check_password

# from django.core.handlers.wsgi import WSGIHandler
# application = WSGIHandler()

from django.contrib.auth.handlers.modwsgi import check_password

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "annotationApp.settings")

application = get_wsgi_application()
