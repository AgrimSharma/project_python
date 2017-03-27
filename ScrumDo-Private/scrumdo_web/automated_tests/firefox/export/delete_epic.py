# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re
from scrumdo_web.automated_tests.selenium.functional_test_case import FunctionalTestCase

class DeleteEpic(FunctionalTestCase):
    def test_19_delete_epic(self):
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
                if self.is_element_present(By.CSS_SELECTOR, "input.button.red"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        driver.find_element_by_css_selector("input.button.red").click()
        alert = driver.switch_to_alert()
        alert.accept()
        for i in range(60):
            try:
                if not self.is_element_present(By.CSS_SELECTOR, "span.epic_edit img"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        try: self.assertFalse(self.is_element_present(By.CSS_SELECTOR, "span.epic_edit img"))
        except AssertionError as e: self.verificationErrors.append(str(e))

if __name__ == "__main__":
    unittest.main()
