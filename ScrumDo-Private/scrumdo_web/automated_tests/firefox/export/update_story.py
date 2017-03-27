# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re
from scrumdo_web.automated_tests.selenium.functional_test_case import FunctionalTestCase

class UpdateStory(FunctionalTestCase):
    def test_21_update_story(self):
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
                if self.is_element_present(By.XPATH, "(//textarea[@id='id_detail'])[2]"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        driver.find_element_by_xpath("(//textarea[@id='id_detail'])[2]").clear()
        driver.find_element_by_xpath("(//textarea[@id='id_detail'])[2]").send_keys("test edit story")
        driver.find_element_by_xpath("//input[@value='Update Story']").click()
        for i in range(60):
            try:
                if self.is_element_present(By.CSS_SELECTOR, "a.edit-story-button > img"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        driver.find_element_by_css_selector("a.edit-story-button > img").click()
        for i in range(60):
            try:
                if self.is_element_present(By.XPATH, "(//textarea[@id='id_detail'])[2]"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        try: self.assertEqual("test edit story", driver.find_element_by_xpath("(//textarea[@id='id_detail'])[2]").get_attribute("value"))
        except AssertionError as e: self.verificationErrors.append(str(e))

if __name__ == "__main__":
    unittest.main()
