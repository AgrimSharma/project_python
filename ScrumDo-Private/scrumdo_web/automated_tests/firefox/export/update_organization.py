# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re
from scrumdo_web.automated_tests.selenium.functional_test_case import FunctionalTestCase

class UpdateOrganization(FunctionalTestCase):
    def test_8_update_organization(self):
        driver = self.driver
        self.login()
        #driver.find_element_by_css_selector("h1").click()
        #driver.find_element_by_link_text("TestOrg").click()
        #driver.find_element_by_link_text("Organization Admin").click()
        driver.get(self.base_url + "/organization/testorg/edit")
        driver.find_element_by_id("id_description").clear()
        driver.find_element_by_id("id_description").send_keys("This is a testing organization")
        driver.find_element_by_css_selector("button.primaryAction").click()
        self.assertTrue('Organization Updated' in driver.find_element(By.TAG_NAME,'body').text)

if __name__ == "__main__":
    unittest.main()
