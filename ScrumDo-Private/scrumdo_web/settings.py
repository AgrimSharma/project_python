# -*- coding: utf-8 -*-

# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
#
# This software is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy (See file COPYING) of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

# Django settings for code project.


# Import all
import sys
from os.path import abspath, dirname, join
from ConfigParser import SafeConfigParser, NoSectionError
from celery.schedules import crontab
import os.path
import posixpath
import logging
import json
import sys
import os
import traceback

CELERYD_TASK_SOFT_TIME_LIMIT = 3000
CELERYD_TASK_TIME_LIMIT = 3000


ALLOWED_HOSTS = ["app.scrumdo.com", "localhost", "scrumdo.com"]

# elasticsearch --config=/usr/local/opt/elasticsearch/config/elasticsearch.yml

AUTH_USER_MODEL = "auth.User"


COMMERCIAL = True  # Now, we only have commercial installations.

DEBUG_TOOLBAR = False

# We have custom organization based timezone logic in place and should not use the default Django TZ implementation.
USE_TZ = False

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))


AVATAR_FONT = os.path.join(PROJECT_ROOT, "../Roboto-Bold.ttf")

sys.path.insert(0, PROJECT_ROOT )

AUTOMATED_EMAIL = 'ScrumDo Robot <noreply@scrumdo.com>'

GETSCRUMBAN_API = "http://www.getscrumban.com/api"


logger = logging.getLogger(__name__)


MIGRATION_MODULES = {
    'mailer': 'apps.migrations_third_party.mailer',
    'avatar': 'apps.migrations_third_party.avatar'
}

# An extra path to look for scrumdo extras on.
EXTRA_PATH = False

DEBUG = False

TEMPLATE_CSS_DEBUG = DEBUG

ADMINS = (
# ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

# This should detect SSL vs HTTP correctly:
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SERVE_MEDIA=True

# Local time zone for this installation. Choices can be found here:
# http://www.postgresql.org/docs/8.1/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
# although not all variations may be possible on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'US/Eastern'

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'en'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'site_media', 'media')

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = '/media/'


SESSION_COOKIE_DOMAIN = ".scrumdo.com"

USE_QUEUE=False

# Absolute path to the directory that holds static files like app media.
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'site_media', 'static')

# URL that handles the static files like app media.
STATIC_URL = '/static/'
SSL_STATIC_URL = '/static/'

# Additional directories which hold static files
STATICFILES_DIRS = (
     os.path.join(PROJECT_ROOT, 'static'),
    )


# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
# ADMIN_MEDIA_PREFIX = posixpath.join(STATIC_URL, "admin/")

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'cl@#$@#!%$^!421464363246y@18*^@-!+$fu^q!sa6yh2^'



AVATAR_DEFAULT_URL =  STATIC_URL +'images/defaultAvatar.png'
AVATAR_GRAVATAR_BACKUP = True


MIDDLEWARE_CLASSES = (
    'apps.avatar.middleware.RemoveVaryCookieMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'apps.django_openid.consumer.SessionConsumer',
    'django.contrib.messages.middleware.MessageMiddleware',
    'rollbar.contrib.django.middleware.RollbarNotifierMiddleware',
    # 'profiling.SqldumpMiddleware',
    # 'profiling.ProfileMiddleware',

    )

PISTON_STREAM_OUTPUT = True

SESSION_ENGINE = "apps.account.session_backend"
SESSION_CACHE_ALIAS = 'default'
SESSION_SERIALIZER = "django.contrib.sessions.serializers.PickleSerializer"

if DEBUG_TOOLBAR:
    MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + ('debug_toolbar.middleware.DebugToolbarMiddleware',)

ROOT_URLCONF = 'urls'





INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.humanize',
    'django.contrib.admin',
    'django.contrib.messages',
    "django.contrib.staticfiles",
    'apps.django_openid',
    'apps.emailconfirmation',
    'mailer',
    'apps.avatar',
    'apps.projects.app.ProjectsApp',
    'apps.attachments',
    'django_markup',
    'apps.account',
    'apps.organizations',
    'apps.activities',
    'django_extensions',
    'apps.extras.app.ExtrasApp',
    'haystack',
    'apps.favorites',
    'apps.pinax',
    'apps.api_v2',
    'piston',
    'apps.scrumdo_mailer',
    'apps.github_integration',
    'apps.realtime',
    'apps.commercial_plugins',
    'apps.subscription.app.SubscriptionApp',
    'apps.email_notifications.app.EmailNotificationApp',
    'bootstrap_toolkit',
    'apps.kanban.app.KanbanApp',
    'apps.form_designer',
    'apps.staff',
    'apps.unsubscribe',
    'bootstrap3',
    'apps.classic',
    'apps.uploader',
    'apps.google_auth',
    'apps.slack',
    'apps.flowdock',
    'apps.hipchat',
    'apps.chat_extras.app.ChatExtrasApp',
    'apps.incoming_email',
    'apps.inbox.app.ScrumDoInboxApp',
    'elasticstack'
)

HAYSTACK_CONNECTIONS = {
   # This is always set in local_settings now, see docker/local_settings.py for example
}

if DEBUG_TOOLBAR:
    INSTALLED_APPS = INSTALLED_APPS + ('apps.debug_toolbar',)




ABSOLUTE_URL_OVERRIDES = {
    "auth.user": lambda o: "/profiles/profile/%s/" % o.username,
    }

MARKUP_FILTER_FALLBACK = 'none'
MARKUP_CHOICES = (
    ('restructuredtext', u'reStructuredText'),
    ('textile', u'Textile'),
    ('markdown', u'Markdown'),)
WIKI_MARKUP_CHOICES = MARKUP_CHOICES

STORY_LINKING_PREFIX_TOKEN = "sd-"


NOTIFICATION_LANGUAGE_MODULE = 'apps.account.Account'

ACCOUNT_OPEN_SIGNUP = True
ACCOUNT_REQUIRED_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = False

EMAIL_CONFIRMATION_DAYS = 2
EMAIL_DEBUG = DEBUG
EMAIL_REGISTRATION_DAYS = 2

# USED FOR AUTOMATION TESTING
EMAIL_DEBUG_REGISTRATION_KEY = "eeeee764a1c04c15877d796e7b464532"
REGISTRATION_TEST_EMAIL = "badaddress@scrumdo.com"

SITE_NAME = "ScrumDo Community Site"
LOGIN_URL = "/account/login/"
LOGIN_REDIRECT_URLNAME = "classic_picker"
LOGIN_POST_CLASSIC_URLNAME = "apps.projects.views.home"

CLASSIC_SITE_URL = "https://www.scrumdo.com/orgs"
IS_CLASSIC = False


EMAIL_HOST='localhost'
EMAIL_HOST_USER=''
EMAIL_HOST_PASSWORD=''
EMAIL_PORT='25'

CONTACT_EMAIL = "help@example.com"
DEFAULT_FROM_EMAIL = 'noreply@example.com'
SERVER_EMAIL = 'noreply@example.com'
SUPPORT_URL = "http://support.example.com/"

GOOGLE_ANALYTICS = False
GOOGLE_ANALYTICS_ACCOUNT = ""

# CACHE_BACKEND = 'locmem://'

INTERNAL_IPS = ('127.0.0.1',)


import socket

try:
    HOSTNAME = socket.gethostname()
except:
    HOSTNAME = 'localhost'

BASE_URL="http://%s" % HOSTNAME
SSL_BASE_URL="https://%s" % HOSTNAME



STATICFILES_FINDERS=("django.contrib.staticfiles.finders.FileSystemFinder",
 		     "django.contrib.staticfiles.finders.AppDirectoriesFinder")

# WIKI_WORD_RE = r".*"

PUBNUB_SUB_KEY = ''
PUBNUB_PUB_KEY = ''
PUBNUB_SEC_KEY = ''

SPREEDLY_PATH = ""
SPREEDLY_SITE_NAME = ""
SPREEDLY_API_TOKEN = ""

KANBAN_ALLOWED=True


FLOWDOCK_CLIENT_ID = ''
FLOWDOCK_CLIENT_SECRET = ''


SLACK_CLIENT_ID = ''
SLACK_CLIENT_SECRET = ''

STORY_EMAIL_ADDRESS = "%d-%s@card.scrumdo.com"
PROJECT_EMAIL_ADDRESS = "%s@project.scrumdo.com"


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(levelname)s (%(filename)s:%(lineno)d) %(message)s -',
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
    },
    'handlers': {
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'loggers': {
        'apps.kanban':{
            'handlers':['console'],
            'propagate': True,
            'level':'INFO',
        },
        'django': {
            'handlers':['console'],
            'propagate': True,
            'level':'INFO',
        },
        'apps.projects': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'werkzeug': {
            'handlers': ['console'],
            'level': 'WARN',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'WARN',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console',],
            'level': 'DEBUG',
        },
        'django.contrib.staticfiles': {
            'handlers': ['console',],
            'level': 'WARN',
            'propagate': False,
        },
        'elasticsearch': {
            'handlers': ['console',],
            'level': 'WARN',
            'propagate': False,
        },
    }
}

TEST_RUNNER = 'django.test.runner.DiscoverRunner'


ROLLBAR = {
    'access_token': '8517446bc42e45aeaa2b36abf126c576',
    'environment': 'development-v2' if DEBUG else 'production-v2',
    'branch': 'production-v2',
    'root': PROJECT_ROOT,
}


CELERYBEAT_SCHEDULE = {
        'purge-inbox': {
            'schedule': crontab(minute=0, hour=0, day_of_week=0),
            'task': 'apps.inbox.tasks.purge_old_inbox_items_job'
        },
        # Records project points logs 4:10AM EST
        'project-points-log': {
            'schedule': crontab(minute=10, hour="6,22"),
            'task': 'apps.projects.tasks.record_all_burnup_charts'
        },

        'calc-kanban-stats': {
            'schedule': crontab(minute=25, hour=4),
            'task': 'apps.kanban.tasks.record_all_project_stats'
        },

        'update-mixpanel': {
            'schedule': crontab(minute=45, hour=4),
            'task': 'apps.projects.tasks.update_mixpanel'
        },

        'site-stats': {
            # Records site project/story/user counts  3:30AM EST
            'schedule': crontab(minute=30, hour=3),
            'task': 'apps.projects.tasks.site_stats'
        },

        'fix-cell-movements': {
            # Check and correct missing cell movement records at 4:00am EST
            'schedule': crontab(minute=0, hour=4),
            'task': 'apps.kanban.tasks.check_cell_movements'
        },

        'subscription-transactions': {
            # Re-updates subscription status & stats  5:30PM EST
            'schedule': crontab(minute=30, hour=5),
            'task': 'apps.subscription.tasks.update_transactions'
        },

        'subscription-stats': {
            # Re-updates subscription status & stats  5:40PM EST
            'schedule': crontab(minute=40, hour=5),
            'task': 'apps.subscription.tasks.update_stats'
        },

        'daily-digest': {
            # Send out the daily digest 6:15PM EST / 11:15PMGMT
            'schedule': crontab(minute=15, hour=23),
            'task': 'apps.email_notifications.tasks.send_daily_digest'
        },

        'iteration-report': {
            # Send out the end of iteration report - 2:15AM EST 7:15AM GMT
            'schedule': crontab(minute=15, hour=2),
            'task': 'apps.email_notifications.tasks.send_iteration_reports'
        },

        'email-notifications': {
            # Send out email notifications every 5 minutes
            'schedule': crontab(minute='*/5'),
            'task': 'apps.email_notifications.tasks.send_notifications'
        },

        'send-email': {
            # Email Sending
            'schedule': crontab(minute='*/4'),
            'task': 'apps.email_notifications.tasks.send_queued_mail'
        },

        'resend-email': {
            'schedule': crontab(minute=1, hour=1),
            'task': 'apps.email_notifications.tasks.retry_deferred'
        },

        'extras-full-sync': {
            # Full Sync extras every 12 hours
            'schedule': crontab(minute=30, hour="1, 13"),
            'task': 'apps.extras.tasks.process_queue'
        },

        'extras-pull': {
            # Do a pull once an hour
            'schedule': crontab(minute=0),
            'task': 'apps.extras.tasks.setup_pull_queue'
        },

        'update-story-index': {
            # Update the last hour's worth of cards in the index every hour.
            'schedule': crontab(minute=25),
            'task': 'apps.projects.tasks.update_solr_1_hour'
        },

        'purge-activities': {
            # Purge activities more than 2 years old  once a week
            'schedule': crontab(minute=0, hour=4, day_of_week=0),
            'task': 'apps.activities.tasks.purge_old'
        },

        'system-duedate-risks': {
            # update duedate risks cache - 1:00AM EST 6:00AM GMT
            'schedule': crontab(minute=0, hour=1),
            'task': 'apps.projects.tasks.rebuildProjectsDuedateRisks'
        },

        'system-aging-risks': {
            # update aging risks cache - 1:00AM EST 6:00AM GMT
            'schedule': crontab(minute=0, hour=1),
            'task': 'apps.projects.tasks.rebuildProjectsAgingRisks'
        },
        'purge-increment-schedules': {
            # Purge epmty increment-schedules every day.
            'schedule': crontab(minute=1, hour=3),
            'task': 'apps.projects.tasks.purgeIncrementSchedules'
        },
        'generate_daily_backlog_snapshot': {
            # Generate daily backlog snapshot every start of the day.
            'schedule': crontab(minute=1, hour=0),
            'task': 'apps.kanban.tasks.generate_daily_backlog_snapshot'
        },
        'archive-inactive-organizations': {
            # Purge inactive organizations more than 6 months once every week
            'schedule': crontab(minute='1', hour=5, day_of_week=0),
            'task': 'apps.subscription.tasks.archive_inactive_organizations'
        },
        'archive-project-past-iterations': {
            # Archive project past iterations based on Project setting
            'schedule': crontab(minute=30, hour=1),
            'task': 'apps.projects.tasks.auto_archive_past_iterations'
        }
    }


ELASTICSEARCH_INDEX_SETTINGS = {
     'settings': {
         "index": {
             "number_of_replicas": 0
         },
         "analysis": {
             "analyzer": {
                 "standard": {
                     "type": "standard",
                     "tokenizer": "none"
                 },
                 "ngram_analyzer": {
                     "type": "custom",
                     "tokenizer": "lowercase",
                     "filter": ["haystack_ngram"]
                 },
                 "edgengram_analyzer": {
                     "type": "custom",
                     "tokenizer": "whitespace",
                     "filter": ["lowercase", "haystack_edgengram"]
                 },
                 "text_ws_analyzer": {
                     "type": "custom",
                     "tokenizer": "whitespace"
                 }
             },
             "tokenizer": {

             },
             "filter": {
                 "haystack_word": {
                     "type": "word_delimiter"
                 },
                 "haystack_ngram": {
                     "type": "nGram",
                     "min_gram": 1,
                     "max_gram": 55
                 },
                 "haystack_edgengram": {
                     "type": "edgeNGram",
                     "min_gram": 1,
                     "max_gram": 55
                 }
             }
         }
     }
 }


ELASTICSEARCH_DEFAULT_NGRAM_SEARCH_ANALYZER = 'whitespace'


# local_settings.py can be used to override environment-specific settings
# like database and email that differ between development and production.
from local_settings import *


if DEBUG:
        TEMPLATES = [
            {
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'DIRS': [os.path.join(PROJECT_ROOT, "templates"),],
                'OPTIONS': {
                    'debug': True,
                    'context_processors': (
                        "django.contrib.auth.context_processors.auth",
                        "django.template.context_processors.debug",
                        "django.template.context_processors.i18n",
                        "django.template.context_processors.media",
                        "django.template.context_processors.request",
                        "django.contrib.messages.context_processors.messages",
                        "apps.projects.context_processors.projects_constants",
                        "apps.account.context_processors.openid",
                        "apps.account.context_processors.account",
                    ),
                    'loaders': [
                        'django.template.loaders.filesystem.Loader',
                        'django.template.loaders.app_directories.Loader',
                    ]
                }
            }
        ]
else:
    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [os.path.join(PROJECT_ROOT, "templates"),],
            'OPTIONS': {
                'context_processors': (
                    "django.contrib.auth.context_processors.auth",
                    "django.template.context_processors.debug",
                    "django.template.context_processors.i18n",
                    "django.template.context_processors.media",
                    "django.template.context_processors.request",
                    "django.contrib.messages.context_processors.messages",
                    "apps.projects.context_processors.projects_constants",
                    "apps.account.context_processors.openid",
                    "apps.account.context_processors.account",
                ),
                'loaders': [
                    ('django.template.loaders.cached.Loader', [
                        'django.template.loaders.filesystem.Loader',
                        'django.template.loaders.app_directories.Loader',
                    ]),
                ]
            }
        }
    ]


if 'test' in sys.argv:
    DATABASES['default'] = {'ENGINE': 'django.db.backends.sqlite3'}


import logging.config
logging.config.dictConfig(LOGGING)

USE_INTERCOM = not DEBUG
INTERCOM_APP_ID = '5pg688sj'

# USE_MIXPANEL = not DEBUG
USE_MIXPANEL = True


AWS_QUERYSTRING_EXPIRE = 1800  # Links will be active for 30 minutes

AWS_REPORTING_BUCKET = AWS_STORAGE_BUCKET_NAME


AUTHENTICATION_BACKENDS = ('auth_backend.EmailOrUsernameModelBackend',
                           'django.contrib.auth.backends.ModelBackend',
                           'apps.github_integration.backends.GithubBackend',
                           'apps.google_auth.backends.GoogleBackend')


SCRUMDO_EXTRAS = ( "apps.commercial_plugins.github_extra.plugin",
                   "apps.commercial_plugins.atdd_extra.plugin",
                  )


PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.CryptPasswordHasher',
)

DATABASE_ENGINE = 'mysql'



PISTON_DISPLAY_ERRORS=not DEBUG
# PISTON_DISPLAY_ERRORS=not DEBUG


# import djcelery
# djcelery.setup_loader()






if DEBUG:
    from django.core.servers.basehttp import WSGIServer
    WSGIServer.request_queue_size = 15
