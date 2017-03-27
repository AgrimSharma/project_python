# Automated end to end tests

These are the full e2e automated tests that actually run inside a browser.

# protractor

Individual tests go into atomic tests

End to end runnable scripts go in test scripts.

# setup

To install test drivers:    

   npm install
   webdriver-manager update  

To start test server:    

   webdriver-manager start  

# Database setup

You don't have to do this to run the conf-batch, because that starts with a completely fresh organization that's created
as part of the test.  But if you want to run a stand-alone test, you need to get your database into a known good state that
has the auto user+organization+project.  Here's one way to do it:

Start from an empty database and then in ./scrumdo_web:

```
 python manage.py migrate
 python manage.py loaddata prod-subscription-plans
 python manage.py loaddata jasmine-tests
 python manage.py loaddata auto-org-with-jasmine
 python manage.py createsuperuser --username=mhughes --email=marc.hughes@scrumdo.com --noinput
```



# run


To run ALL the tests:

   protractor conf/conf-batch.coffee --host=https://app.scrumdo.com  
   protractor conf/conf-batch.coffee --host=http://localhost:8000


To run a single test (see note about Database setup above):

   protractor conf/conf-board-sort.coffee --host=http://marc.scrumdo.com  
   protractor cont/conf-login.coffee
   etc...
