# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re
from scrumdo_web.automated_tests.selenium.functional_test_case import FunctionalTestCase

class SwitchOrganization(FunctionalTestCase):
    def test_41_switch_organization(self):
        driver = self.driver
        self.login()
        driver.find_element_by_xpath("//a[contains(@href, '/organization/create/')]").click()
        driver.find_element_by_css_selector("#id_name").clear()
        driver.find_element_by_css_selector("#id_name").send_keys("NewOrg")
        driver.find_element_by_xpath("//button[@type='submit']").click()
        driver.find_element_by_link_text("Free Plan").click()
        driver.find_element_by_link_text("NewOrg").click()
        driver.find_element_by_link_text("Switch Organization").click()
        driver.find_element_by_xpath("//a[contains(@href, '/organization/testorg/dashboard')]").click()
        try: self.assertEqual("TestOrg Dashboard", driver.find_element_by_xpath("//div[@id='organization-body-holder']/h1").text)
        except AssertionError as e: self.verificationErrors.append(str(e))


if __name__ == "__main__":
    unittest.main()
