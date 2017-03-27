Visit [ScrumDo.com](http://www.ScrumDo.com) to use it.

# Getting Started

1. Clone the repo locally.  

  git clone git@github.com:ScrumDoLLC/ScrumDo-Private.git

2. Create a virtual environment

    virtualenv env

3. Activate that environment (Do this every time you work on ScrumDo!)

    source env/bin/activate


4. Install external requirements after cd scrumdo_web.

    pip install -r requirements.txt

    OSX Trouble shooting tip:
    Run in terminal if you have import issues: xcode-select --install


5. Create a local_settings.py file in scrumdo_web that lists all your site specific settings.

    cd scrumdo_web  
    cp local_settings.template.py local_settings.py   
    edit local_settings.py

If you're first starting out, you probably want to get a copy from another developer.


6. Sync your database

    python manage.py migrate  
    python manage.py createsuperuser  
    python manage.py loaddata prod-subscription-plans  


7. Run your server

    python manage.py runserver

There is also an offline job server that runs.  It's best to leave it running while you're developing to make sure those tasks work.  BUT - it doesn't auto-reload code.  So if you change any tasks (or code they depend on) you have to restart it. Have to be in scrumdo_web.

 | celery worker -l info -A celeryconfig
 
You can run both of those commands within your IDE's debugger.  I highly recommend PyCharm.


# Redis

You'll need redis to perform some server operations.

On OSX:

| brew install redis

Then just run

| redis-server

Whenever you want to use it. You can safely run it in the background.

# Elastic Search

Elastic search indexes our data and allows for searching and filtering to function.  The easiest way to get set up and running is to create a development index on our production elastic search server.  To do that, add the config below to local_settings.py.

You have to set an INDEX_NAME and it has to start with the prefix dev.  For instance, I use devmarc - pick a name that won't collide with others.

```python
import elasticsearch
from sdawsauth import StrBasedAWS4Auth
awsauth = StrBasedAWS4Auth(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, 'us-east-1', 'es')
HAYSTACK_CONNECTIONS = {
    'default': {
            'ENGINE': 'elasticstack.backends.ConfigurableElasticSearchEngine',
            'URL': 'https://search-scrumdo-jxxa3g4l7u7qkef44l3p2xrbda.us-east-1.es.amazonaws.com/',
            'INDEX_NAME': '',
            'KWARGS': {
                'port': 443,
                'http_auth': awsauth,
                'use_ssl': True,
                'verify_certs': True,
                'connection_class': elasticsearch.RequestsHttpConnection,
        }
    }
}
```

After that's done, rebuild your index once:

`python manage.py rebuild_index`

Now you should be able to use search/filtering.  You have to run celery if you want your index to stay up to date when you create/edit cards.  Otherwise you can just run

`python manage.py update_index`

Try not to index tens of thousands of cards at a time, it is our production search server and performance could be hurt.  Normal usage should be fine.

This assumes you're using the scrumdo-dev AWS access keys.

Note: Please make sure that the node js version is compatible with protractor@2 (preferably v0.12.0) 

# Every time you develop...

Make sure the following is running:

1. MySql
2. Redis
3. ScrumDo Celery
4. ScrumDo Server
5. grunt watch


