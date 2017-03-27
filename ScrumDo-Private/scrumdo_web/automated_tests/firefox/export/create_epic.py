# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re
from scrumdo_web.automated_tests.selenium.functional_test_case import FunctionalTestCase

class CreateEpic(FunctionalTestCase):
    def test_17_create_epic(self):
        driver = self.driver
        self.login()
        driver.find_element_by_css_selector("h1").click()
        driver.find_element_by_link_text("TestOrg").click()
        driver.find_element_by_link_text("Projects").click()
        driver.get(self.base_url + "/projects/project/testproject/")
        driver.get(self.base_url + "/projects/project/testproject/epics")
        driver.find_element_by_id("ember303").click()
        for i in range(60):
            try:
                if self.is_element_present(By.ID, "id_points"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        driver.find_element_by_id("id_points").clear()
        driver.find_element_by_id("id_points").send_keys("12")
        driver.execute_script("$('#id_summary').val('test epic')")
        driver.find_element_by_css_selector("button.primaryAction").click()
        for i in range(60):
            try:
                if self.is_element_present(By.CSS_SELECTOR, "span.epic_edit img"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        self.assertEquals('test epic' in driver.find_element(By.TAG_NAME,'body').text, True)

if __name__ == "__main__":
    unittest.main()
