import os
import sys

import newrelic.agent
newrelic.agent.initialize('/etc/newrelic/newrelic.ini')

os.environ['DJANGO_SETTINGS_MODULE'] = 'scrumdo_web.settings'

import django.core.handlers.wsgi as w
application = w.WSGIHandler()

application = newrelic.agent.wsgi_application()(application)

