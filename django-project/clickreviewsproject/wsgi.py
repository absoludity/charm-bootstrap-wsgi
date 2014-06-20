import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "clickreviewsproject.settings")

extra_paths = [
    '/srv/click-reviews.ubuntu.com/code/current/branches/scaclient/',
    '/srv/click-reviews.ubuntu.com/code/current/branches/piston-mini-client/',
    '/srv/click-reviews.ubuntu.com/code/current/branches/django-piston/',
]
sys.path.extend(extra_paths)

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
