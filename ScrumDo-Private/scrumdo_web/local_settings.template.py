import sys
from os.path import abspath, dirname, join
import logging
import settings

MY_HOSTNAME="http://localhost:9000"  # either set up a DNS redirect, or set this to http://localhost:8080/
ADMINS = ( ('YOUR NAME', 'YOUR EMAIL ADDRESS'), )


# Set this to true to add google analytics to the pages, not for use in development
# GOOGLE_ANALYTICS = False
# GOOGLE_ANALYTICS_ACCOUNT = 'UA-XXXXXXX-X'

# SUPPORT_URL = "http://your support url"
# DEFAULT_FROM_EMAIL = 'your from email @ your domain . com'
# SERVER_EMAIL = DEFAULT_FROM_EMAIL
# SITE_NAME = "Your site name"


# CONTACT_EMAIL = DEFAULT_FROM_EMAIL
# EMAIL_HOST='smtp.something.com'
# EMAIL_HOST_USER='username'
# EMAIL_HOST_PASSWORD='password'
# EMAIL_PORT='587'
# EMAIL_USE_TLS=True

SSL_BASE_URL=MY_HOSTNAME
BASE_URL=MY_HOSTNAME

MIXPANEL_TOKEN=""

# For some real time communication stuff
# HOOKBOX_HOST = "http://localhost:2728" 
# HOOKBOX_SECRET = "your secret"

# File attachment storage ------------------------
# To use Amazon S3...
# DEFAULT_FILE_STORAGE = 'storages.backends.s3.S3Storage'
# AWS_DEFAULT_ACL = 'authenticated-read'
# AWS_QUERYSTRING_ACTIVE = True
# AWS_CALLING_FORMAT = 2 # CallingFormat.SUBDOMAIN
# AWS_ACCESS_KEY_ID = 'YOUR ACCESS KEY'
# AWS_SECRET_ACCESS_KEY = 'YOUR SECRET KEY'
# AWS_STORAGE_BUCKET_NAME = 'YOUR BUCKET NAME' 
    

# Extras SQS queue --------------------------------
# This uses Amazon SQS, you could also use rabbitmq or similar
# USE_QUEUE=True
# BROKER_TRANSPORT = 'sqs'
# BROKER_TRANSPORT_OPTIONS = {
#     'region': 'us-east-1',
#     'polling_interval': 5
# }
# BROKER_USER = AWS_ACCESS_KEY_ID
# BROKER_PASSWORD = AWS_SECRET_ACCESS_KEY
# CELERY_DEFAULT_QUEUE = 'scrumdo-extras-prod'    
#     
# CELERYD_CONCURRENCY = 1
# CELERY_QUEUES = {
#     CELERY_DEFAULT_QUEUE: {
#         'exchange': CELERY_DEFAULT_QUEUE,
#         'binding_key': CELERY_DEFAULT_QUEUE,
#     }
# }
    

MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'

# Haystack
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.simple_backend.SimpleEngine'
    }
}

# Database config ----------------------------------------
#DATABASE_ENGINE = 'mysql'    # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
#DATABASE_NAME = 'scrumdo'       # Or path to database file if using sqlite3.
#DATABASE_USER = 'root'             # Not used with sqlite3.
#DATABASE_PASSWORD = 'root'         # Not used with sqlite3.


#django 1.4 database config
DATABASES = {
        "default": {
        "ENGINE": "django.db.backends.mysql", # Add "postgresql_psycopg2", "postgresql", "mysql", "sqlite3" or "oracle".
        "NAME": "scrumdo",                       # Or path to database file if using sqlite3.
        "USER": "root",                             # Not used with sqlite3.
        "PASSWORD": "root",                         # Not used with sqlite3.
        "HOST": "localhost",                             # Set to empty string for localhost. Not used with sqlite3.
        "ATOMIC_REQUESTS": True
#        "PORT": "",                             # Set to empty string for default. Not used with sqlite3.
    }
}


import djcelery
djcelery.setup_loader()
