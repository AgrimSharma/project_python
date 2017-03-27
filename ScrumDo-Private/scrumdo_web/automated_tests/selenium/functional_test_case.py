# -*- coding: utf-8 -*-
import os
import base64
import httplib
import logging
import time, datetime
from urllib2 import URLError
from selenium import webdriver
from django.conf import settings
from django.utils import unittest
from pyvirtualdisplay import Display
from selenium.webdriver.common.by import By
from django_jenkins.runner import XMLTestResult
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.common.exceptions import TimeoutException, ElementNotVisibleException

try: import json
except ImportError:
    import simplejson as json

tslogger = logging.getLogger("apps")

SAUCE_USER = "scrumdo"
SAUCE_KEY = "d18b9ad4-d171-44ff-a647-b286028a63ec"

def setUpModule():
    tslogger.info("%s.setUpModule"%__name__)

def tearDownModule():
    tslogger.info("%s.tearDownModule"%__name__)


class Singleton(object):
    __instance__ = None

    def __new__(cls, *a, **kw):
        if Singleton.__instance__ is None:
            Singleton.__instance__ = object.__new__(cls, *a, **kw)
            cls._Singleton_instance = Singleton.__instance__
        return Singleton.__instance__

    def _drop_it(self):
        self.__instance__ = None

class MyRemoteDriver(Singleton, webdriver.Remote):
    pass

class MyFirefoxDriver(Singleton, webdriver.Firefox):
    pass

class ScrumDoTestResult(XMLTestResult):
    """
    Test result browser screen shot taking addition
    """
    def makeBrowserContentScreenShot(self, test):
        """
        Save screen shot as file
        """
        filename = settings.PROJECT_ROOT + "/automated_tests/results/screenshots/%s-%s.png"\
            % (datetime.datetime.now().strftime("%Y%m%d%H%M%S"), self.test_method_name(test))
        try:
            created = test.get_screenshot_as_file(filename)
            #if created: tslogger.debug("'%s' screen shot file created" % filename)
        except URLError: tslogger.debug("'%s' screen shot failed to be created" % filename)


    def addError(self, test, err):
        """
        Saves image of test errors
        """
        self.makeBrowserContentScreenShot(test)
        super(ScrumDoTestResult, self).addError(test, err)

    def addFailure(self, test, err):
        """
        Saves image of test failures
        """
        self.makeBrowserContentScreenShot(test)
        super(ScrumDoTestResult, self).addFailure(test, err)


class FunctionalTestCase(unittest.TestCase):
    login_session = None
    verificationErrors = []
    base_url = "http://localhost:9000"

    @classmethod
    def setUpClass(cls):
        tslogger.info("%s.setUpClass" % cls.__module__)
        cls.driver = MyFirefoxDriver()
        cls.driver.implicitly_wait(10)
        cls.driver.maximize_window()
        cls.mouse = webdriver.ActionChains(cls.driver)

    @classmethod
    def tearDownClass(cls):
        tslogger.info("%s.tearDownClass" % cls.__module__)
        cls.driver.quit()

    def defaultTestResult(self):
        return ScrumDoTestResult()

    def _environ(self):
        """ Runtime environment variables settings configuration """
        self.base_cls = os.environ.get('TEST_CASE_CLASS', self.__class__ )
        if 'VIRTUALDISPLAY' in os.environ: # in case no x-window on linux
            self.display = Display(backend='xvfb').start()

    def _driver(self):
        """ Firefox driver initialization to implement separately for other browsers,
            Accept custom environment vars FIREFOX_PROFILEPATH and FIREFOX_BINARYPATH
        """
        if 'FIREFOX_PROFILEPATH' not in os.environ: ffp = webdriver.FirefoxProfile()
        else: ffp = webdriver.FirefoxProfile(profile_directory=os.environ['FIREFOX_PROFILEPATH'])

        ffp.set_preference("browser.download.folderList", 2)
        ffp.set_preference("browser.download.dir", settings.TEST_RESULTS)
        ffp.set_preference("browser.download.manager.showWhenStarting", False)
        ffp.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/vnd.ms-excel")

        if 'FIREFOX_BINARYPATH' not in os.environ: ffb = None
        else: ffb = FirefoxBinary(firefox_path=os.environ['FIREFOX_BINARYPATH'])

        return webdriver.Firefox(firefox_profile=ffp,firefox_binary=ffb,timeout=10)

    def login(self):
        driver = self.driver
        if self.login_session is None:
            driver.get(self.base_url + "/account/login")
            driver.find_element_by_id("id_username").clear()
            driver.find_element_by_id("id_username").send_keys("scrumdoselenium")
            driver.find_element_by_id("id_password").clear()
            driver.find_element_by_id("id_password").send_keys("scrumdotesting")
            driver.find_element_by_xpath("//input[@value='Log In »']").click()
            self.login_session = driver.session_id
            tslogger.info("%s.login()" % self.__module__)
        else: driver.get(self.base_url)
        return self.driver

    def logout(self):
        if self.login_session:
            self.driver.get(self.base_url + "/account/logout")
            self.login_session = None

    def create_organization(self, name="TestOrg", subscription=False):
        driver = self.driver
        driver.get(self.base_url + "/organization/create/")
        driver.find_element_by_id("id_name").clear()
        driver.find_element_by_id("id_name").send_keys(name)
        driver.find_element_by_css_selector("button.primaryAction").click()

        if subscription:
            driver.get("%s/subscription/%s?first_time=1" % (
                self.base_url,'-'.join(name.split()).lower()))
            driver.execute_script(
                "window.scrollTo(0,document.body.scrollHeight/2);")
            driver.find_elements_by_css_selector(
                "table.subscription_table td.subscribe_button_cell a.button.green")[0].click()

            driver.find_element_by_id("credit_card_first_name").clear()
            driver.find_element_by_id("credit_card_first_name").send_keys("Scrum")
            driver.find_element_by_id("credit_card_last_name").clear()
            driver.find_element_by_id("credit_card_last_name").send_keys("Do")
            driver.find_element_by_id("credit_card_number").clear()
            driver.find_element_by_id("credit_card_number").send_keys("4222222222222")
            driver.find_element_by_id("credit_card_verification_value").clear()
            driver.find_element_by_id("credit_card_verification_value").send_keys("343")
            Select(driver.find_element_by_id("credit_card_month")).select_by_visible_text("7 - July")
            Select(driver.find_element_by_id("credit_card_year")).select_by_visible_text("2014")
            driver.find_element_by_name("purchase_button").click()
            driver.find_element_by_link_text("Continue...").click()
            driver.find_element_by_link_text("Continue to your dashboard").click()

        return driver

    def create_project(self, name="TestProject", org_id=1):
        driver = self.driver
        driver.get(self.base_url + "/projects/create/?org=%d" % org_id)
        driver.find_element_by_id("id_name").clear()
        driver.find_element_by_id("id_name").send_keys(name)
        driver.find_element_by_css_selector("button.primaryAction").click()
        return driver

    def create_epic(self):
        raise NotImplementedError

    def create_story(self, url, detail):
        driver = self.driver
        driver.get(self.base_url + url)
        story_summary_fld = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID,"id_summary")))
        story_summary_fld.clear(); story_summary_fld.send_keys("test story")
        driver.find_element_by_id("add_button").click()
        return driver

    def create_iteration(self):
        raise NotImplementedError

    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException, e: return False
        return True

    def setUp(self):
        pass
        #self._environ()
        #tslogger.info("%s.%s.setUp" % (self.__class__.__module__,self.__class__.__name__))

    def tearDown(self):
        if 'VIRTUALDISPLAY' in os.environ: self.display.stop()
        self.assertEqual([], self.verificationErrors)
        self.login_session = None
        #tslogger.info("%s.%s.tearDown" % (self.__class__.__module__,self.__class__.__name__))

    def spin_assert(self, msg, assertion):
        for i in xrange(60):
            try:
                self.assertTrue(assertion())
                return
            except Exception, e:
                pass
            time.sleep(1)
        self.fail(msg)

    def spin_wait_for_text_present(self, text):
        self.spin_assert("waiting for text '%s' to appear" % text,
                         lambda: self.driver.is_text_present(text))

    def __getattribute__(self, name):
        """Include driver attributes lookup"""
        try: attr = object.__getattribute__(self, name)
        except AttributeError:
            try: attr = self.driver.__getattribute__(name)
            except AttributeError:
                raise ValueError("no such test method in %s: %s" %
                  (self.__class__, methodName))

        return attr

class SauceTestResult(XMLTestResult):
    """Test result reporting pass/fail status automatically"""
    def reportPassFail(self, test, passed=True):
        """
        Sauce doesn't really know what the test in your end does with the browser, let us know
        """
        base64string = base64.encodestring('%s:%s' % (SAUCE_USER, SAUCE_KEY))[:-1]
        connection = httplib.HTTPConnection('saucelabs.com')
        connection.request('PUT', '/rest/v1/%s/jobs/%s' % (SAUCE_USER, test.driver.session_id),
                           json.dumps({'passed': passed}), headers={"Authorization": "Basic %s" % base64string})
        result = connection.getresponse()
        return result.status == 200

    def addSuccess(self, test):
        """
        Reports pass fail to sauce
        """
        super(SauceTestResult, self).addSuccess(test)
        self.reportPassFail(test, passed=True)

    def addError(self, test, err):
        """
        Reports pass fail to sauce
        """
        super(SauceTestResult, self).addError(test, err)
        self.reportPassFail(test, passed=False)

    def addFailure(self, test, err):
        """
        Reports pass fail to sauce
        """
        super(SauceTestResult, self).addFailure(test, err)
        self.reportPassFail(test, passed=False)


class Selenium2OnSauce(FunctionalTestCase):
    def _driver1(self):
        firefox_profile = webdriver.FirefoxProfile()
        firefox_profile.set_preference("browser.download.folderList", 2)
        firefox_profile.set_preference("browser.download.dir", settings.TEST_RESULTS)
        firefox_profile.set_preference("browser.download.manager.showWhenStarting", False)
        firefox_profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/vnd.ms-excel")

        desired_capabilities = webdriver.DesiredCapabilities.FIREFOX
        desired_capabilities.update({'version': '17',
                                     'platform': 'Linux',
                                     'acceptSslCerts': True,
                                     'build': 'dev@'+self.base_url,
                                     'name': self.id().split('.')[-1]})

        return webdriver.Remote(desired_capabilities = desired_capabilities, browser_profile = firefox_profile,
                      command_executor = "http://scrumdo:d18b9ad4-d171-44ff-a647-b286028a63ec@ondemand.saucelabs.com:80/wd/hub")

    def _driver2(self):
        #firefox_profile = FirefoxProfile()
        #firefox_profile.set_preference("browser.download.folderList", 2)
        #firefox_profile.set_preference("browser.download.dir", settings.TEST_RESULTS)
        #firefox_profile.set_preference("browser.download.manager.showWhenStarting", False)
        #firefox_profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/vnd.ms-excel")

        desired_capabilities = webdriver.DesiredCapabilities.FIREFOX
        #desired_capabilities['version'] = '3.6'
        #desired_capabilities['platform'] = 'Windows 2003'
        #desired_capabilities['name'] = 'Testing Selenium 2 in Python at Sauce'
        desired_capabilities.update({'version': '17',
                                     'platform': 'Linux',
                                     'build': 'dev@'+self.base_url,
                                     'name': self.id().split('.')[-1]})

        return webdriver.Remote(desired_capabilities = desired_capabilities,
                      command_executor = "http://scrumdo:d18b9ad4-d171-44ff-a647-b286028a63ec@saucelabs.com:4444/wd/hub")


    def defaultTestResult(self):
        return SauceTestResult()

    def setUp(self):
        tslogger.info("%s.%s.setUp" % (self.__class__.__module__,self.__class__.__name__))
        desired_capabilities = webdriver.DesiredCapabilities.FIREFOX
        desired_capabilities['version'] = '19'
        desired_capabilities['platform'] = 'Linux'
        desired_capabilities['build'] = 'for Haritha'
        working_directory = self.id().split(".")
        desired_capabilities['name'] = working_directory[2]
        desired_capabilities['tags'] = working_directory[:2]
        desired_capabilities["custom-data"] = \
                                   {"release": "1.0",
                                    "staging": True,
                                    "execution_number": 1,
                                    "commit": "0k392a9dkjr",
                                    "server": self.base_url,
                                    "parent-tunnel": "scrumdo"}

        self.driver = MyRemoteDriver(
            desired_capabilities=desired_capabilities,
            command_executor="http://scrumdo:d18b9ad4-d171-44ff-a647-b286028a63ec@ondemand.saucelabs.com:80/wd/hub"
        )
        self.driver.implicitly_wait(30)
        self.driver.maximize_window()
        self.mouse = webdriver.ActionChains(self.driver)

    def setUp1(self):
        from selenium import webdriver
        fp = webdriver.FirefoxProfile()
        # set something on the profile...
        driver = webdriver.Remote(desired_capabilities=webdriver.DesiredCapabilities.FIREFOX, browser_profile=fp)

    def tearDown(self):
        print("Link to your job: https://saucelabs.com/jobs/%s" % self.driver.session_id)
        super(Selenium2OnSauce, self).tearDown()