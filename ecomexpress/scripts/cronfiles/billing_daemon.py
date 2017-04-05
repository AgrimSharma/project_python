import os
import sys
import datetime

os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')

# http://www.gavinj.net/2012/06/building-python-daemon-process.html
#standard python libs
import logging
import time

#third party libs
from daemon import runner

from billing.provisional_billing import process_provisional_billqueue
from billing.generate_bill import process_billqueue

# To run this file: python scripts/cronfiles/billing_daemon.py start
# To stop this file: python scripts/cronfiles/billing_daemon.py stop

def reset_database_connection():  
    from django import db  
    db.close_connection()  

class App():
    
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path =  '/var/run/testdaemon/billing_daemon1.pid'
        self.pidfile_timeout = 5
            
    def run(self):
        while True:
            #Main code goes here ...
            reset_database_connection()
            process_provisional_billqueue()
            process_billqueue()
            time.sleep(300)

app = App()
logger = logging.getLogger("DaemonLog")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.FileHandler("/var/log/testdaemon/billing_daemon1.log")
handler.setFormatter(formatter)
logger.addHandler(handler)

daemon_runner = runner.DaemonRunner(app)
#This ensures that the logger file handle does not get closed during daemonization
daemon_runner.daemon_context.files_preserve=[handler.stream]
daemon_runner.do_action()
