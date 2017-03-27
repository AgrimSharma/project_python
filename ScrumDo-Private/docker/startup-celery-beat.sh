#!/bin/bash
# We call it extras, but it really just processes all queues

cd /srv/scrumdo/scrumdo_web
export C_FORCE_ROOT='true'
exec celery beat -l info -A celeryconfig
