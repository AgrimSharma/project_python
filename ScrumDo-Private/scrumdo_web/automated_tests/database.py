from django.core import management
management.call_command('syncdb', verbosity=2, interactive=False)
management.call_command('migrate', verbosity=2, interactive=False)
management.call_command('loaddata', 'scrumdo_web/automated_tests/fixture/initial_data.json', verbosity=2)



