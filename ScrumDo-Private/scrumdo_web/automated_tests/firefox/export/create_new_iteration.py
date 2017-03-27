# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re
from scrumdo_web.automated_tests.selenium.functional_test_case import FunctionalTestCase

class CreateNewIteration(FunctionalTestCase):
    def test_42_create_new_iteration(self):
        driver = self.driver
        self.login()
        #driver.get(self.base_url + "/projects/project/testproject/stories/")
        #driver.find_element_by_id("addIterationButton").click()
        driver.get(self.base_url + "/projects/project/testproject/iteration_create")
        driver.find_element_by_id("id_name").clear()
        driver.find_element_by_id("id_name").send_keys("TestIteration")
        driver.find_element_by_id("id_start_date").clear()
        driver.find_element_by_id("id_start_date").send_keys("2012-07-08")
        #driver.find_element_by_id("id_start_date").click()
        #driver.find_element_by_link_text("8").click()
        driver.find_element_by_id("id_end_date").clear()
        driver.find_element_by_id("id_end_date").send_keys("2012-07-29")
        #driver.find_element_by_id("id_end_date").click()
        #driver.find_element_by_link_text("29").click()
        driver.find_element_by_css_selector("button.primaryAction").click()
        self.assertTrue('TestIteration' in driver.find_element(By.TAG_NAME,'body').text)

if __name__ == "__main__":
    unittest.main()
