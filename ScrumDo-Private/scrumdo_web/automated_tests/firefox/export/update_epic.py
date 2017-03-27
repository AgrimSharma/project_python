# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re
from scrumdo_web.automated_tests.selenium.functional_test_case import FunctionalTestCase

class UpdateEpic(FunctionalTestCase):
    def test_18_update_epic(self):
        driver = self.driver
        self.login()
        driver.find_element_by_css_selector("h1").click()
        driver.find_element_by_link_text("TestOrg").click()
        driver.find_element_by_link_text("Projects").click()
        driver.get(self.base_url + "/projects/project/testproject/")
        driver.get(self.base_url + "/projects/project/testproject/epics")
        for i in range(60):
            try:
                if self.is_element_present(By.CSS_SELECTOR, "span.epic_edit img"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        driver.find_element_by_css_selector("span.epic_edit img").click()
        for i in range(60):
            try:
                if self.is_element_present(By.ID, "id_detail"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        driver.find_element_by_id("id_detail").clear()
        driver.find_element_by_id("id_detail").send_keys("edit epic test")
        driver.find_element_by_css_selector("button.primaryAction").click()
        for i in range(60):
            try:
                if self.is_element_present(By.CSS_SELECTOR, "span.epic_edit img"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        for i in range(60):
            try:
                if self.is_element_present(By.ID, "id_detail"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        driver.find_element_by_css_selector("span.epic_edit img").click()
        try: self.assertEqual("edit epic test", driver.find_element_by_id("id_detail").get_attribute("value"))
        except AssertionError as e: self.verificationErrors.append(str(e))

if __name__ == "__main__":
    unittest.main()
