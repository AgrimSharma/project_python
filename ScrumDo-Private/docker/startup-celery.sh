#!/bin/bash

# NO LONGER USED - see high/med/low scripts instead

cd /srv/scrumdo/scrumdo_web
export C_FORCE_ROOT='true'
exec celery worker -l info -A celeryconfig -Q scrumdo-prod-high
