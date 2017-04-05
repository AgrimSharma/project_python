import os
import os.path
import sys

sys.path.append('/home/web/ecomm.prtouch.com')
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress')
print sys.path
os.environ['PYTHON_EGG_CACHE'] = '/home/web/ecomm.prtouch.com/.python-eggs'
os.environ['DJANGO_SETTINGS_MODULE'] = 'ecomexpress.settings'


import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
