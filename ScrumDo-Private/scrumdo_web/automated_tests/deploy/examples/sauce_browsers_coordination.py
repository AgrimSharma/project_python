from threading import Thread
from selenium import selenium
import time
try:
    import json
except ImportError:
    import simplejson as json

USERNAME = "USERNAME"
ACCESS_KEY = "ACCESS-KEY"

def get_sauce_browser(os="Windows 2003", browser="firefox", version="."):
    config = {"username": USERNAME,
              "access-key": ACCESS_KEY,
              "os": os,
              "browser": browser,
              "browser-version": version,
              "job-name": "%s %s on %s" % (browser, version, os),
             }
    return selenium('saucelabs.com',
                    4444,
                    json.dumps(config),
                    'http://saucelabs.com')

b1 = get_sauce_browser(version="3.0")
b2 = get_sauce_browser(version="3.5")
b3 = get_sauce_browser(version="3.6")

browsers = [b1, b2, b3]
browsers_waiting = []

def get_browser_and_wait(browser, browser_num):
    print "starting browser %s" % browser_num
    browser.start()
    browser.open("/")
    browsers_waiting.append(browser)
    print "browser %s ready" % browser_num
    while len(browsers_waiting) < len(browsers):
        print "browser %s sending heartbeat while waiting" % browser_num
        browser.open("/")
        time.sleep(3)

thread_list = []
for i, browser in enumerate(browsers):
    t = Thread(target=get_browser_and_wait, args=[browser, i + 1])
    thread_list.append(t)
    t.start()

for t in thread_list:
    t.join()

print "all browsers ready"
for i, b in enumerate(browsers):
    print "browser %s's title: %s" % (i + 1, b.get_title())
    b.stop()
