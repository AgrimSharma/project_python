# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re
from scrumdo_web.automated_tests.selenium.functional_test_case import FunctionalTestCase

class CreateAStory(FunctionalTestCase):
    def test_20_create_a_story(self):
        driver = self.driver
        self.login()
        driver.find_element_by_css_selector("h1").click()
        driver.find_element_by_link_text("TestOrg").click()
        driver.find_element_by_link_text("Projects").click()
        driver.get(self.base_url + "/projects/project/testproject/")
        driver.find_element_by_link_text("TestProject").click()
        driver.find_element_by_link_text("Story List").click()
        driver.find_element_by_id("id_summary").clear()
        driver.find_element_by_id("id_summary").send_keys("test story")
        driver.find_element_by_id("add_button").click()
        driver.find_element_by_link_text("TestProject").click()
        driver.find_element_by_link_text("Story List").click()
        self.assertEquals('test story' in driver.find_element(By.TAG_NAME,'body').text, True)

if __name__ == "__main__":
    unittest.main()
