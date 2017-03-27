# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re
from scrumdo_web.automated_tests.selenium.functional_test_case import FunctionalTestCase

class UpdateStoryStatus(FunctionalTestCase):
    def test_update_story_status(self):
        driver = self.driver
        self.login()
        driver.find_element_by_css_selector("h1").click()
        driver.find_element_by_link_text("TestOrg").click()
        driver.find_element_by_link_text("Projects").click()
        driver.get(self.base_url + "/projects/project/testproject/")
        driver.find_element_by_link_text("TestProject").click()
        driver.find_element_by_link_text("Story List").click()
        driver.find_element_by_css_selector("a.edit-story-button > img").click()
        for i in range(60):
            try:
                if self.is_element_present(By.XPATH, "//*[@id=\"id_status_1\"]"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        driver.find_element_by_id("id_status_1").click()
        driver.find_element_by_xpath("//input[@value='Update Story']").click()
        driver.find_element_by_link_text("TestProject").click()
        driver.find_element_by_link_text("Story List").click()
        self.assertEquals('Doing' in driver.find_element(By.TAG_NAME,'body').text, True)

        driver.find_element_by_css_selector("a.edit-story-button > img").click()
        for i in range(60):
            try:
                if self.is_element_present(By.XPATH, "//*[@id=\"id_status_2\"]"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        driver.find_element_by_id("id_status_2").click()
        for i in range(60):
            try:
                if self.is_element_present(By.XPATH, "//input[@value='Update Story']"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        driver.find_element_by_xpath("//input[@value='Update Story']").click()
        driver.find_element_by_link_text("TestProject").click()
        driver.find_element_by_link_text("Story List").click()
        self.assertEquals('Reviewing' in driver.find_element(By.TAG_NAME,'body').text, True)

        driver.find_element_by_css_selector("a.edit-story-button > img").click()
        for i in range(60):
            try:
                if self.is_element_present(By.XPATH, "//*[@id=\"id_status_3\"]"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        driver.find_element_by_id("id_status_3").click()
        for i in range(60):
            try:
                if self.is_element_present(By.XPATH, "//input[@value='Update Story']"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        driver.find_element_by_xpath("//input[@value='Update Story']").click()
        driver.find_element_by_link_text("TestProject").click()
        driver.find_element_by_link_text("Story List").click()
        self.assertEquals('Done' in driver.find_element(By.TAG_NAME,'body').text, True)

if __name__ == "__main__":
    unittest.main()
