# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re
from scrumdo_web.automated_tests.selenium.functional_test_case import FunctionalTestCase

class DublicateStory(FunctionalTestCase):
    def test_23_dublicate_story(self):
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

        driver.find_element_by_css_selector("a.edit-story-button > img").click()
        for i in range(60):
            try:
                if self.is_element_present(By.XPATH, "//input[@value='Duplicate Story']"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        driver.find_element_by_xpath("//input[@value='Duplicate Story']").click()
        driver.find_element_by_link_text("TestProject").click()
        driver.find_element_by_link_text("Story List").click()
        self.assertEquals('#2' in driver.find_element(By.TAG_NAME,'body').text, True)

if __name__ == "__main__":
    unittest.main()
