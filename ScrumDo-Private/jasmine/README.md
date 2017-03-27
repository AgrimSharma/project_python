# Jasmine/Frisby Tests

These are a set of jasmine based tests using the frisby library to test our REST api.

# Setup:

* npm install
* npm install -g jasmine-node
* npm install --save-dev frisby


# Run Tests:

Set up your local_config.js based on local_config.sample

Run once:

jasmine-node  .

Watch test files (doesn't watch source files):

jasmine-node . --color --autotest


# This is how the integration server runs:

(on a blank DB)

in ./scrumdo_web:
````
 python manage.py migrate
 python manage.py loaddata prod-subscription-plans
 python manage.py loaddata jasmine-tests
 python manage.py createsuperuser --username=mhughes --email=marc.hughes@scrumdo.com --noinput
 python manage.py runserver &
````

in ./jasmine:
````
 cp local_settings.ci local_settings.js
 jasmine-node  .
````
