# Django settings for ecomm project.
#python -m smtpd -n -c DebuggingServer localhost:1025
import os
from django.core.cache import cache
#from track_me.views import custom_show_toolbar

PROJECT_ROOT = os.path.abspath(os.path.dirname(__name__))
PROJECT_ROOT_DIR = '/home/web/ecomm.prtouch.com/ecomexpress/'

PDF_HOME = PROJECT_ROOT + 'static/uploads/billing/'

DEBUG = False
DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
      ('Girish', 'girishw@prtouch.com'),
      ('Onkar','onkar@prtouch.com'),
    # ('Your Name', 'your_email@example.com'),
)

FILE_UPLOAD_TEMP_DIR = os.path.join(PROJECT_ROOT,'/home/web/ecomm.prtouch.com/ecomexpress/static/uploads')
FILE_UPLOAD_MAX_MEMORY_SIZE = 1


EMAIL_HOST = 'localhost'
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_PORT = 25
EMAIL_USE_TLS = False
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
DEFAULT_FROM_EMAIL='support@ecomexpress.in'

#CACHE_BACKEND = 'memcached://127.0.0.1:11211/'


#  mysql -h mzdbeeplv1.ctoyhb7trpv7.us-east-1.rds.amazonaws.com -uecomm ecomm -p
MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'ecomm',                      # Or path to database file if using sqlite3.
        #'USER': 'root',                      # Not used with sqlite3.
        #'PASSWORD': 'root12',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.

        'USER': 'root',                      # Not used with sqlite3.
        'PASSWORD': 'root12',                  # Not used with sqlite3.
        #'HOST': 'localhost' ,                      # Set to empty string for localhost. Not used with sqlite3.
        #'PASSWORD': 'm1z2d3b4eepl',                  # Not used with sqlite3.
        #'HOST': 'mzdbeeplsmall.ctoyhb7trpv7.us-east-1.rds.amazonaws.com',                      # Set to empty string for localhost. Not used with sqlite3.
        #'USER':'ecommprtouch',
        #'HOST': '54.173.24.100',                      

        #'PASSWORD': 'e1c2o3m4r1e2p3o4r5!',                  
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
        'OPTIONS': {
               "init_command": "SET storage_engine=INNODB",
        }  

    },'local_ecomm': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'ecomm',                      # Or path to database file if using sqlite3.
        'USER': 'root',                      # Not used with sqlite3.
        'PASSWORD': 'root12',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
       #'USER': 'ecommprtouch',                      # Not used with sqlite3.
       #'PASSWORD': 'e1c2o3m4r1e2p3o4r5!',                  # Not used with sqlite3.
       #'HOST': '54.164.140.76',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to e
    }

}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}



# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Asia/Calcutta'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'
SITE_ID = 1

DATE_INPUT_FORMATS = ('%Y-%m-%d', '%d/%m/%Y', '%d/%m/%y', '%b %d %Y')
# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

#INTERNAL_IPS = ('127.0.0.1','109.75.164.136')
# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/ecomm.prtouch.com/static/"
STATIC_ROOT = os.path.join(PROJECT_ROOT,'/home/web/ecomm.prtouch.com/ecomexpress/static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)
ADMIN_MEDIA_PREFIX = '/static/admin/' 
# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '@#y1&amp;zy8*bxqxqq7_w(6(p8evmu^#*l$rko_9wgf3sv^wl^ve2'


# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
  #  'debug_toolbar.middleware.DebugToolbarMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_sorting.middleware.SortingMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'privateviews.middleware.LoginRequiredMiddleware',
    'authentication.middleware.restrict_login.UserRestrictMiddleware',
    #'authentication.middleware.observe_url.VerifyAccessMiddleware',
)

ROOT_URLCONF = 'ecomexpress.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'ecomexpress.wsgi.application'

TEMPLATE_DIRS = (
     os.path.join(PROJECT_ROOT,'/home/web/ecomm.prtouch.com/ecomexpress/templates')            
    #'/var/www/ecomm.prtouch.com/ecomm/templates'
     #'/var/www/ecomm.prtouch.com/ecomm/templates'
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

LOGIN_URL='/'

TEMPLATE_CONTEXT_PROCESSORS = (
         "django.contrib.auth.context_processors.auth",
         "django.core.context_processors.debug",
         "django.core.context_processors.i18n",
         "django.core.context_processors.media",
         "django.core.context_processors.request",
         'django.core.context_processors.static',
         'django.contrib.messages.context_processors.messages',)


PUBLIC_VIEWS = [
    'django.contrib.auth.views.password_reset_done',
    'django.contrib.auth.views.password_reset',
    'django.contrib.auth.views.password_reset_confirm',
    'django.contrib.auth.views.password_reset_complete',
 ]


PUBLIC_PATHS = [

    '^/static', # Uses the 'direct_to_template' generic view
]

INSTALLED_APPS = (
    'admin_tools',
    'admin_tools.theming',
    'admin_tools.menu',
    'admin_tools.dashboard',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
#    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',
    #'django.contrib.admindocs',
    'crispy_forms',
    'django.contrib.admin',
    'django.contrib.humanize',
    'django_sorting',
    'billing',
    'customer',
    'pagination',
    'authentication',
    'pickup',
    'airwaybill',
    'south',
    'smsapp',
    'location',
    'ecomm_admin',
    'service_centre',
    'track_me',
    'delivery',
    'hub',
    'reports',
    'dateutil',
    'mobi_api',
    'macaddress',
    'nimda',
    'api',
    'octroi',
    'wb_entry_tax',
    'custom_entry_tax',
    'chargemanager',
    'integration_services',
    'operations',
    'product_master',
    'dcdashboard',
    'generic',
    'apiv2',
    'djcelery',
    'amazon_api',
   # 'debug_toolbar'
    'endless_pagination',
    'easy_maps',
    'shacti_api',
    'mongoadmin',
)

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': os.path.join(os.path.dirname(__file__), 'whoosh_index'),
    },
}

#def testdt(request):
def custom_show_toolbar(request):
    try:
      if request.user.employeemaster.employee_code == '63826':
          return True
      return False
    except:
 
       return False

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}



#print request.user
INTERNAL_IPS = ('127.0.0.1','109.75.164.136','109.75.164.255')

MIDDLEWARE_CLASSES += (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    )

INSTALLED_APPS += (
        'debug_toolbar',
    )

DEBUG_TOOLBAR_PANELS = (
        'debug_toolbar.panels.version.VersionDebugPanel',
        'debug_toolbar.panels.timer.TimerDebugPanel',
        'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
        'debug_toolbar.panels.headers.HeaderDebugPanel',
        #'debug_toolbar.panels.profiling.ProfilingDebugPanel',
        'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
        'debug_toolbar.panels.sql.SQLDebugPanel',
        'debug_toolbar.panels.template.TemplateDebugPanel',
        'debug_toolbar.panels.cache.CacheDebugPanel',
        'debug_toolbar.panels.signals.SignalDebugPanel',
        'debug_toolbar.panels.logger.LoggingPanel',
    )

#from track_me.views import custom_show_toolbar
#DEBUG_TOOLBAR_CONFIG = {
#    'SHOW_TOOLBAR_CALLBACK': lambda req: True,
#}

#def custom_show_toolbar(request):
  #  if request.user.is_superuser:
  #      return True
 #   return False

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False, 
   'SHOW_TOOLBAR_CALLBACK': custom_show_toolbar,
}

#DEBUG_TOOLBAR_CONFIG = {

#    return HttpResponse("chk")
#    'SHOW_TOOLBAR_CALLBACK': custom_show_toolbar,
#}  

# Local variables
ROOT_URL = 'http://ecomm.prtouch.com'
BILL_FILE = PROJECT_ROOT + STATIC_URL + 'uploads/billing/bill.xls'

CRISPY_TEMPLATE_PACK = 'bootstrap'

# CELERY SETTINGS
BROKER_URL = 'amqp://localhost//'
CELERY_RESULT_BACKEND = 'amqp://'

