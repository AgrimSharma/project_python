# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re
from scrumdo_web.automated_tests.selenium.functional_test_case import FunctionalTestCase

class CreateAProject(FunctionalTestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30)
        self.base_url = "http://localhost:9000"
        self.verificationErrors = []

    def test_9_create_a_project(self):
        driver = self.driver
        self.login()
        #for i in range(60):
        #    try:
        #        if self.is_element_present(By.CSS_SELECTOR, "ul.organization_list > a.button.large.green"): break
        #    except: pass
        #    time.sleep(1)
        #else: self.fail("time out")
        #driver.find_element_by_id("delete_button").click()
        driver.find_element_by_css_selector("div.organization_picker > a").click()
        driver.find_element_by_link_text("New Project").click()
        driver.find_element_by_id("id_name").clear()
        driver.find_element_by_id("id_name").send_keys("TestProject")
        driver.find_element_by_css_selector("button.primaryAction").click()
        self.assertEquals('Project Created' in driver.find_element(By.TAG_NAME,'body').text, True)

    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
