# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re
from scrumdo_web.automated_tests.selenium.functional_test_case import FunctionalTestCase

class UpdateProjectSettings(FunctionalTestCase):
    def test_10_update_project_settings(self):
        driver = self.driver
        self.login()
        driver.find_element_by_css_selector("div.organization_picker > a").click()
        driver.find_element_by_link_text("TestOrg").click()
        driver.find_element_by_link_text("Projects").click()
        driver.find_element_by_css_selector("a.block_link > h2").click()
        driver.find_element_by_link_text("TestProject").click()
        driver.find_element_by_link_text("Project Admin").click()
        driver.find_element_by_id("id_description").clear()
        driver.find_element_by_id("id_description").send_keys("this is a test project")
        driver.find_element_by_css_selector("button.primaryAction").click()
        self.assertTrue('Project options Saved.' in driver.find_element(By.TAG_NAME,'body').text)

if __name__ == "__main__":
    unittest.main()
