#!/bin/bash


python /srv/scrumdo/scrumdo_web/manage.py collectstatic --noinput
exec uwsgi /srv/scrumdo/scrumdo_web/uwsgi.ini
