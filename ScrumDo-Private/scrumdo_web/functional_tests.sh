#!/bin/sh

if [ -d $PIP_VIRTUALENV_BASE ]; then
  echo "**> virtualenv exists"
  . $PIP_VIRTUALENV_BASE/bin/activate
else
  echo  "**> creating virtualenv"
  virtualenv $PIP_VIRTUALENV_BASE

  echo "**> setup requirements"
  . $PIP_VIRTUALENV_BASE/bin/activate
  pip install -r $WORKSPACE/requirements.txt
fi


echo "**> setup database settings"
cd $WORKSPACE/scrumdo_web
echo "DATABASE_ENGINE='sqlite3'
DATABASE_NAME='$WORKSPACE/scrumdo_web/automated_tests/database.db'
DATABASE_SUPPORTS_TRANSACTIONS=True" >> settings.py




echo "**> setup local_settings.py"
cd $WORKSPACE/scrumdo_web
cp local_settings.template.py local_settings.py

echo "**> setup github login settings"
echo "GITHUB_AUTH_URL = 'https://github.com/login/oauth/authorize'
GITHUB_TOKEN_URL = 'https://github.com/login/oauth/access_token'
GITHUB_CLIENT_ID = '0c3732e1b15eb95f46c9'
GITHUB_SECRET = 'd36eb2b1a3238398edc91c2c41b95bbeac91400c'" >> local_settings.py

echo "**> setup speedly settings"
echo "SPREEDLY_PATH='https://spreedly.com/scrumdo-beta'
SPREEDLY_SITE_NAME='scrumdo-beta'
SPREEDLY_API_TOKEN='1a8d8d75826e9eccecab666aae3ba30239c6e09d'" >> local_settings.py

echo "**> setup pusher settings"
echo "PUSHER_APP_ID = '18998'
PUSHER_KEY = 'a8a14760469f309ba40c'
PUSHER_SECRET = '82ce5d378c5746ad69cd'" >> local_settings.py

echo "Starting web server"
python manage.py runserver localhost:9000 > runserver.log 2>&1 &