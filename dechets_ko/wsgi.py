"""
WSGI config for dechets_ko project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dechets_ko.settings')

application = get_wsgi_application()