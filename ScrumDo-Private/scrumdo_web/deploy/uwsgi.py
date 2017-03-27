# pinax.wsgi is configured to live in projects/backlog-site/deploy.
try:
    import requests
    # We only have single newrelic license, so only use it on this IP...
    ip = requests.get('http://169.254.169.254/latest/meta-data/local-ipv4', timeout=3).text
    if ip == '10.0.46.71':
        import newrelic.agent
        newrelic.agent.initialize('/srv/scrumdo/newrelic.ini')
        application = newrelic.agent.WSGIApplicationWrapper(application)
except:
    pass

import os
import sys
import logging

os.environ["CELERY_LOADER"] = "django"

logger = logging.getLogger('')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


# redirect sys.stdout to sys.stderr for bad libraries like geopy that uses
# print statements for optional import exceptions.
sys.stdout = sys.stderr

from os.path import abspath, dirname, join
from site import addsitedir

sys.path.insert(0, abspath(join(dirname(__file__), "../../")))
sys.path.insert(0, abspath(join(dirname(__file__), "../")))

os.environ["DJANGO_SETTINGS_MODULE"] = "settings"

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

