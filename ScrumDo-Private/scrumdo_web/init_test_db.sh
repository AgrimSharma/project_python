#!/bin/bash
set -e
python manage.py migrate --no-input
python manage.py loaddata prod-subscription-plans
python manage.py loaddata jasmine-tests
python manage.py loaddata auto-org-with-jasmine
python manage.py createsuperuser --username=mhughes --email=marc.hughes@scrumdo.com
