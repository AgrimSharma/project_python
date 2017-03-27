# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re
from scrumdo_web.automated_tests.selenium.functional_test_case import FunctionalTestCase

class DeleteProject(FunctionalTestCase):
    def test_11_delete_project(self):
        driver = self.driver
        self.login()
        driver.find_element_by_css_selector("div.organization_picker > a").click()
        driver.find_element_by_link_text("TestOrg").click()
        driver.find_element_by_link_text("Projects").click()
        driver.find_element_by_css_selector("a.block_link > h2").click()
        driver.find_element_by_link_text("TestProject").click()
        driver.find_element_by_link_text("Project Admin").click()
        driver.find_element_by_link_text("Admin").click()
        driver.find_element_by_link_text("Delete project").click()
        driver.find_element_by_css_selector("#delete_project_form > input[type=\"submit\"]").click()
        self.assertTrue('Project TestProject deleted.' in driver.find_element(By.TAG_NAME,'body').text)

if __name__ == "__main__":
    unittest.main()
