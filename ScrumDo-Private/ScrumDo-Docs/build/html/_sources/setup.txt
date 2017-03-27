Setup Guide
=========================

Installing dependencies
-----------------------
***************
On Ubuntu 16.04
***************
sudo apt-get install **mysql-server**
root passwd: **root**

sudo apt-get install **virtualenv libmysqlclient-dev python-dev libxml2-dev npm ruby ruby-dev**

.. seealso:: the node npm installer will most probably not work, so you have to make the following link:
   
   **sudo ln -s /usr/bin/nodejs /usr/bin/node**


Configure the Environment
-------------------------

1. Clone the repo locally.
::

git clone git@github.com:ScrumDoLLC/ScrumDo-Private.git


2. Create a virtual environment

    virtualenv env

#. Activate that environment (**Do this every time you work on ScrumDo!**)

    source env/bin/activate

#. Install external requirements after cd scrumdo_web.

    pip install -r requirements.txt

    OSX Trouble shooting tip: Run in terminal if you have import issues: xcode-select --install

    Create a local_settings.py file in scrumdo_web that lists all your site specific settings.
    .. note:
    To get an working example ask in the Slack Codegenesys development channel.

    cd scrumdo_web
    cp local_settings.template.py local_settings.py
    edit local_settings.py

If you're first starting out, you probably want to get a copy from another developer.

    Sync your database

    python manage.py syncdb --noinput
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py loaddata prod-subscription-plans

    Run your server

    python manage.py runserver

There is also an offline job server that runs. It's best to leave it running while you're developing to make sure those tasks work. BUT - it doesn't auto-reload code. So if you change any tasks (or code they depend on) you have to restart it. Have to be in scrumdo_web.

| celery worker -l info -A celeryconfig

You can run both of those commands within your IDE's debugger. I highly recommend PyCharm.