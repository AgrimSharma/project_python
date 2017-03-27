# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re
from scrumdo_web.automated_tests.selenium.functional_test_case import FunctionalTestCase

class DeleteStory(FunctionalTestCase):
    def test_22_delete_story(self):
        driver = self.driver
        self.login()
        driver.find_element_by_css_selector("h1").click()
        driver.find_element_by_link_text("TestOrg").click()
        driver.find_element_by_link_text("Projects").click()
        driver.get(self.base_url + "/projects/project/testproject/")
        driver.find_element_by_link_text("TestProject").click()
        driver.find_element_by_link_text("Story List").click()
        for i in range(60):
            try:
                if self.is_element_present(By.CSS_SELECTOR, "a.edit-story-button > img"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        driver.find_element_by_css_selector("a.edit-story-button > img").click()
        for i in range(60):
            try:
                if self.is_element_present(By.XPATH, "//input[@value='Delete Story']"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        driver.find_element_by_xpath("//input[@value='Delete Story']").click()
        alert = driver.switch_to_alert()
        alert.accept()
        for i in range(60):
            try:
                if not self.is_element_present(By.CSS_SELECTOR, "a.edit-story-button > img"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        try: self.assertFalse(self.is_element_present(By.CSS_SELECTOR, "a.edit-story-button > img"))
        except AssertionError as e: self.verificationErrors.append(str(e))

if __name__ == "__main__":
    unittest.main()
