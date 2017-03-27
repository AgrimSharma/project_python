#!/usr/bin/env python
#-.- coding=utf8 -.-
import unittest
from selenium import webdriver
import os
from selenium.webdriver.common.proxy import Proxy


class Selenium2OnSauce(unittest.TestCase):

    def setUp(self):
        desired_capabilities = {'browserName': "firefox"}
        desired_capabilities['platform'] = 'LINUX'
        desired_capabilities['version'] = '14'
        desired_capabilities['name'] = "Using your own proxy with Sauce"

        proxy = Proxy()
        proxy.http_proxy = 'your.proxy.server:1234'
        proxy.add_to_capabilities(desired_capabilities)

        desired_capabilities['public'] = True
        self.driver = webdriver.Remote(desired_capabilities=desired_capabilities,
                                       command_executor="http://sso:%s@saucelabs.com:4444/wd/hub" % os.environ['KEY'])
        self.driver.implicitly_wait(10)

    def test_basic(self):
        driver = self.driver
        driver.get("http://saucelabs.com")
        assert "Sauce" in driver.title

    def tearDown(self):
        try:
            self.driver.quit()
        except:
            pass
