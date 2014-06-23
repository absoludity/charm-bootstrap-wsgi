#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "clickreviewsproject.settings")
    extra_paths = [
        '/srv/click-reviews.ubuntu.com/code/current/branches/scaclient/',
        '/srv/click-reviews.ubuntu.com/code/current/branches/piston-mini-client/',
        '/srv/click-reviews.ubuntu.com/code/current/branches/django-piston/',
    ]
    sys.path.extend(extra_paths)

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
