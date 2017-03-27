from S3 import CallingFormat
import os

HOSTNAME = os.environ.get("HOST_NAME", "app.scrumdo.com")

SESSION_COOKIE_NAME = os.environ.get("SESSION_COOKIE_NAME", "sessionid")

ALLOWED_HOSTS = [HOSTNAME, "app.scrumdo.com", "scrumdo.com", "192.168.99.100", "localhost", "localhost:3035", "localhost:8000"]


import requests
EC2_PRIVATE_IP = None
try:
    EC2_PRIVATE_IP = requests.get('http://169.254.169.254/latest/meta-data/local-ipv4', timeout=10).text
    print "EC2_PRIVATE_IP %s" % EC2_PRIVATE_IP
except requests.exceptions.RequestException:
    print "Could not find EC2 Private IP"

if EC2_PRIVATE_IP:
    # This is so the ELB can contact us for the health check on the private IP
    ALLOWED_HOSTS.append(EC2_PRIVATE_IP)
    print "ALLOWED_HOSTS: %s" % ALLOWED_HOSTS


GOOGLE_ANALYTICS = True
GOOGLE_ANALYTICS_ACCOUNT = 'UA-19817142-1'
DEBUG = False
#TEMPLATE_DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY','dlfkjdsklfj9048ifuoljdlikfj')

CONTACT_EMAIL = "support@scrumdo.com"
DEFAULT_FROM_EMAIL = 'noreply@scrumdo.com'
SERVER_EMAIL = 'noreply@scrumdo.com'

SUPPORT_URL = "http://support.scrumdo.com/"

SITE_NAME = "ScrumDo"

STATIC_ROOT = "/srv/scrumdo-static"

dir = os.path.abspath( __file__ )
dir = os.path.dirname(dir)

from static_url import STATIC_URL
# STATIC_URL = os.environ.get("STATIC_PATH","")

SSL_STATIC_URL = STATIC_URL

DEFAULT_BASE_URL="https://%s" % HOSTNAME
BASE_URL=os.environ.get("BASE_URL", DEFAULT_BASE_URL)
SSL_BASE_URL=BASE_URL


EMAIL_HOST='smtp.mandrillapp.com'
EMAIL_HOST_USER='scrumdo'
EMAIL_HOST_PASSWORD=os.environ.get("EMAIL_HOST_PASSWORD", "" )
EMAIL_PORT='587'
EMAIL_USE_TLS=True

DATABASE_HOST = os.environ.get('DATABASE_HOST','')
DATABASE_PORT = os.environ.get('DATABASE_PORT','')
DATABASE_NAME = os.environ.get('DATABASE_NAME','')
DATABASE_USER = os.environ.get('DATABASE_USER','')
DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD','')

DATABASES = {
        "default": {
        "ENGINE": "django.db.backends.mysql", # Add "postgresql_psycopg2", "postgresql", "mysql", "sqlite3" or "oracle".
        "NAME": DATABASE_NAME,                       # Or path to database file if using sqlite3.
        "USER": DATABASE_USER,                             # Not used with sqlite3.
        "PASSWORD": DATABASE_PASSWORD,                         # Not used with sqlite3.
        "HOST": DATABASE_HOST,                             # Set to empty string for localhost. Not used with sqlite3.
        "PORT": DATABASE_PORT,
        "ATOMIC_REQUESTS": True,
        "CONN_MAX_AGE": 300,
        'OPTIONS' : {
            'init_command': 'SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED'
        }

    }
}


AVATAR_GRAVATAR_DEFAULT = SSL_STATIC_URL + "images/defaultAvatar.png"
AVATAR_DEFAULT_URL = AVATAR_GRAVATAR_DEFAULT
GRAVATAR_URL_PREFIX="https://secure.gravatar.com/"
AWS_S3_SECURE_URLS = True

import sys
import os.path
import settings
from os.path import abspath, dirname, join


THIS_PATH = abspath(dirname(__file__))



SPREEDLY_SITE_NAME="scrumdo"
SPREEDLY_API_TOKEN=os.environ.get('SPREEDLY_API_TOKEN','')
SPREEDLY_PATH="https://subs.pinpayments.com/scrumdo"



# DEFAULT_FILE_STORAGE = 'storages.backends.s3.S3Storage'
DEFAULT_FILE_STORAGE = 'storage_backend.SimpleNameS3Storage'

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID','')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY','')


# logger.info('AWS_ACCESS_KEY_ID %s' % AWS_ACCESS_KEY_ID)
# logger.info('AWS_SECRET_ACCESS_KEY %s' % AWS_SECRET_ACCESS_KEY)

AWS_STORAGE_BUCKET_NAME = os.environ.get('ATTACHMENTS_BUCKET', 'scrumdo-attachments') #'scrumdo-attachments'
AWS_DEFAULT_ACL = 'authenticated-read'
AWS_QUERYSTRING_ACTIVE = True
AWS_CALLING_FORMAT = CallingFormat.SUBDOMAIN
SPREEDLY_PLAN_IDS = { "bronze":10165, "silver":10166, "gold":10167, "platinum":11292, "bronze_yearly":11073, "silver_yearly":11074, "gold_yearly":11075, "platinum_yearly":11291 }


from sdawsauth import StrBasedAWS4Auth
import elasticsearch
awsauth = StrBasedAWS4Auth(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, 'us-east-1', 'es')
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'apps.projects.search_backend.ScrumDoConfigurableElasticSearchEngine',
        'URL': os.environ.get('ELASTIC_SEARCH_ENDPOINT', ''),
        'INDEX_NAME': os.environ.get('ELASTIC_SEARCH_INDEX',''),
        'TIMEOUT': 60 * 5,
        'KWARGS': {
            'port': 443,
            'http_auth': awsauth,
            'use_ssl': True,
            'verify_certs': True,
            'connection_class': elasticsearch.RequestsHttpConnection,
        }
    }
}


USE_QUEUE=True
BROKER_TRANSPORT = 'sqs'
BROKER_TRANSPORT_OPTIONS = {
    'region': 'us-east-1',
    'polling_interval': 3
}
BROKER_USER = AWS_ACCESS_KEY_ID
BROKER_PASSWORD = AWS_SECRET_ACCESS_KEY

CELERYD_CONCURRENCY = 2
CELERYD_MAX_TASKS_PER_CHILD = 500


CELERY_QUEUE_HIGH  = os.environ.get('CELERY_QUEUE_HIGH', 'scrumdo-prod-high')
CELERY_QUEUE_MED = os.environ.get('CELERY_QUEUE_MED', 'scrumdo-prod-med')
CELERY_QUEUE_LOW = os.environ.get('CELERY_QUEUE_LOW', 'scrumdo-prod-low')

CELERY_DEFAULT_QUEUE = CELERY_QUEUE_MED
CELERY_DEFAULT_EXCHANGE = CELERY_QUEUE_MED
CELERY_DEFAULT_ROUTING_KEY = CELERY_QUEUE_MED

# NOTE: if you stop using pickle, things break because datetime is not serializable by the other and is
# passed in several places (such as slack notifications)
CELERY_ACCEPT_CONTENT = ['json', 'msgpack', 'yaml', 'pickle']
CELERY_TASK_SERIALIZER = 'pickle'

CELERY_QUEUES = {
    CELERY_QUEUE_HIGH: {
        'exchange': CELERY_QUEUE_HIGH,
        'binding_key': CELERY_QUEUE_HIGH,
    },

    CELERY_QUEUE_MED: {
        'exchange': CELERY_QUEUE_MED,
        'binding_key': CELERY_QUEUE_MED,
    },

    CELERY_QUEUE_LOW: {
        'exchange': CELERY_QUEUE_LOW,
        'binding_key': CELERY_QUEUE_LOW,
    },

}

CELERY_ROUTES = {
    'apps.realtime.tasks.send_messages': {'queue': CELERY_QUEUE_HIGH},

    'apps.activities.tasks.purge_old': {'queue': CELERY_QUEUE_LOW},
    'apps.email_notifications.tasks.retry_deferred': {'queue': CELERY_QUEUE_LOW},
    'apps.email_notifications.tasks.send_daily_digest': {'queue': CELERY_QUEUE_LOW},
    'apps.email_notifications.tasks.send_iteration_reports': {'queue': CELERY_QUEUE_LOW},
    'apps.extras.tasks.processExtrasQueue': {'queue': CELERY_QUEUE_LOW},
    'apps.extras.tasks.process_queue': {'queue': CELERY_QUEUE_LOW},
    'apps.extras.tasks.setup_pull_queue': {'queue': CELERY_QUEUE_LOW},
    'apps.kanban.tasks.check_cell_movements': {'queue': CELERY_QUEUE_LOW},
    'apps.kanban.tasks.rebuildStepMovements': {'queue': CELERY_QUEUE_LOW},
    'apps.kanban.tasks.record_all_project_stats': {'queue': CELERY_QUEUE_LOW},
    'apps.kanban.tasks.reset_project_age_values': {'queue': CELERY_QUEUE_LOW},
    'apps.projects.tasks.calculateStoryRollUpTime': {'queue': CELERY_QUEUE_LOW},
    'apps.projects.tasks.record_all_burnup_charts': {'queue': CELERY_QUEUE_LOW},
    'apps.projects.tasks.resetStoryTagsLabel': {'queue': CELERY_QUEUE_LOW},
    'apps.projects.tasks.scheduledCalculateMacroStats': {'queue': CELERY_QUEUE_LOW},
    'apps.projects.tasks.site_stats': {'queue': CELERY_QUEUE_LOW},
    'apps.projects.tasks.updateProjectIndexes': {'queue': CELERY_QUEUE_LOW},
    'apps.projects.tasks.update_mixpanel': {'queue': CELERY_QUEUE_LOW},
    'apps.projects.tasks.update_solr_1_hour': {'queue': CELERY_QUEUE_LOW},
    'apps.stats.tasks.logEvent': {'queue': CELERY_QUEUE_LOW},
    'apps.subscription.tasks.update_stats': {'queue': CELERY_QUEUE_LOW},
    'apps.subscription.tasks.update_transactions': {'queue': CELERY_QUEUE_LOW},
    'apps.unsubscribe.tasks.unsubscribeEmailAddress': {'queue': CELERY_QUEUE_LOW},
    'apps.projects.calculation.calculateReleasePoints': {'queue': CELERY_QUEUE_LOW},
    'apps.projects.calculation.delayedCalculateProject': {'queue': CELERY_QUEUE_LOW},
    'apps.email_notifications.tasks.send_queued_mail': {'queue': CELERY_QUEUE_LOW},

}

# NOTE: These are on the default medium-priority queue:

# apps.commercial_plugins.tasks.generateATDDFile
# apps.email_notifications.tasks.sendChatMentionEmail
# apps.email_notifications.tasks.sendMentionEmail
# apps.email_notifications.tasks.send_notifications
# apps.flowdock.tasks.on_attachment_added
# apps.flowdock.tasks.on_card_created
# apps.flowdock.tasks.on_card_modified
# apps.flowdock.tasks.on_card_moved
# apps.flowdock.tasks.on_comment_posted
# apps.flowdock.tasks.send_flowdock_message
# apps.github_integration.tasks.handle_issues_webhook
# apps.github_integration.tasks.syncronize_teams
# apps.hipchat.tasks.on_attachment_added
# apps.hipchat.tasks.on_card_created
# apps.hipchat.tasks.on_card_modified
# apps.hipchat.tasks.on_card_moved
# apps.hipchat.tasks.on_comment_posted
# apps.hipchat.tasks.send_flowdock_message
# apps.inbox.tasks.on_attachment_added
# apps.inbox.tasks.on_comment_posted
# apps.inbox.tasks.on_epic_created
# apps.inbox.tasks.on_epic_updated
# apps.inbox.tasks.on_iteration_created
# apps.inbox.tasks.on_iteration_updated
# apps.inbox.tasks.on_project_created
# apps.inbox.tasks.on_story_created
# apps.inbox.tasks.on_story_deleted
# apps.inbox.tasks.on_story_moved
# apps.inbox.tasks.on_story_updated
# apps.inbox.tasks.on_task_created
# apps.inbox.tasks.on_task_status_changed
# apps.inbox.tasks.on_task_updated
# apps.inbox.tasks.purge_old_inbox_items_job
# apps.kanban.tasks.convertClassicProject
# apps.organizations.tasks.exportOrganization
# apps.projects.tasks.exportIteration
# apps.projects.tasks.exportProject
# apps.projects.tasks.indexStory
# apps.projects.tasks.sendStoryAddedSignals
# apps.projects.tasks.updateSolr
# apps.scrumdo_mailer.tasks.sendEmails
# apps.slack.tasks.on_attachment_added
# apps.slack.tasks.on_card_created
# apps.slack.tasks.on_card_modified
# apps.slack.tasks.on_card_moved
# apps.slack.tasks.on_comment_posted
# apps.slack.tasks.send_slack_message




GITHUB_CLIENT_ID = os.environ.get('GITHUB_CLIENT_ID', '')
GITHUB_SECRET = os.environ.get('GITHUB_SECRET', '')
GITHUB_AUTH_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"


ADMINS = (
    ('Marc Hughes', 'marc.hughes@scrumdo.com'),
    ('Ajay Reddy', 'ajay@scrumdo.com')
)

MANAGERS = ADMINS

# Production pubnub credentials
PUBNUB_SUB_KEY = os.environ.get('PUBNUB_SUB_KEY','')
PUBNUB_PUB_KEY = os.environ.get('PUBNUB_PUB_KEY','')
PUBNUB_SEC_KEY = os.environ.get('PUBNUB_SEC_KEY','')

PUSHER_APP_ID = ''
PUSHER_KEY = ''
PUSHER_SECRET = ''

BASECAMP_CALLBACK_URL="https://www.scrumdo.com/basecamp_next/auth_callback"
BASECAMP_CLIENT_ID=os.environ.get('BASECAMP_CLIENT_ID','')
BASECAMP_SECRET_KEY=os.environ.get('BASECAMP_SECRET_KEY','')

GOOGLE_OAUTH = {
  "CLIENT_ID": os.environ.get('GOOGLE_CLIENT_ID',''),
  "EMAIL_ADDRESS": os.environ.get('GOOGLE_EMAIL_ADDRESS',''),
  "CLIENT_SECRET": os.environ.get('GOOGLE_CLIENT_SECRET',''),
  "REDIRECT_URI": "https://app.scrumdo.com/openid/login/googleauth/oauth2callback/",
  "OPENID_REALM": "https://app.scrumdo.com/openid/"
}

SLACK_CLIENT_ID = os.environ.get('SLACK_CLIENT_ID','')
SLACK_CLIENT_SECRET = os.environ.get('SLACK_CLIENT_SECRET','')

FLOWDOCK_CLIENT_ID = os.environ.get('FLOWDOCK_CLIENT_ID','')
FLOWDOCK_CLIENT_SECRET = os.environ.get('FLOWDOCK_CLIENT_SECRET','')

MIXPANEL_TOKEN = os.environ.get('MIXPANEL_TOKEN','')

CACHES = {
	'default': {
		"BACKEND": "django_redis.cache.RedisCache",
		'LOCATION': os.environ.get("REDIS_SERVER", ''),
		'OPTIONS': {
            'IGNORE_EXCEPTIONS': True,
			'DB': os.environ.get("REDIS_DB", 1),
			'PASSWORD': '',
			'PARSER_CLASS': 'redis.connection.HiredisParser',
			'CONNECTION_POOL_CLASS': 'redis.BlockingConnectionPool',
			'CONNECTION_POOL_CLASS_KWARGS': {
				'max_connections': 50,
				'timeout': 20,
			}
		},
	},
}

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
ROLLBAR = {
    'access_token': '8517446bc42e45aeaa2b36abf126c576',
    'environment': 'production-v2-ecs',
    'branch': 'production-v2',
    'root': PROJECT_ROOT,
}


if 'test' in sys.argv[1:] or 'jenkins' in sys.argv[1:]:
    CELERY_ALWAYS_EAGER = True
