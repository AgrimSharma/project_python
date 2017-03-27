# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re
from scrumdo_web.automated_tests.selenium.functional_test_case import FunctionalTestCase

class ArchiveProject(FunctionalTestCase):
    def test_12_archive_project(self):
        driver = self.driver
        self.login()
        driver.find_element_by_css_selector("div.organization_picker > a").click()
        driver.find_element_by_link_text("TestOrg").click()
        driver.find_element_by_link_text("Projects").click()
        driver.find_element_by_link_text("New Project").click()
        driver.find_element_by_id("id_name").clear()
        driver.find_element_by_id("id_name").send_keys("TestProjectArchive")
        driver.find_element_by_css_selector("button.primaryAction").click()
        driver.find_element_by_link_text("TestProjectArchive").click()
        driver.find_element_by_link_text("Project Admin").click()
        driver.find_element_by_link_text("Admin").click()
        driver.find_element_by_id("archiveFormButton").click()
        self.assertTrue('This project is archived.' in driver.find_element(By.TAG_NAME,'body').text)

if __name__ == "__main__":
    unittest.main()
