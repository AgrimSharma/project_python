import os
import sys
import logging

os.environ["CELERY_LOADER"] = "django"
os.environ["DJANGO_SETTINGS_MODULE"] = "settings"

logger = logging.getLogger('')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)



from os.path import abspath, dirname, join

sys.path.insert(0, abspath(join(dirname(__file__), "../../")))
sys.path.insert(0, abspath(join(dirname(__file__), "../")))


from django.core.handlers.wsgi import WSGIHandler
application = WSGIHandler()
