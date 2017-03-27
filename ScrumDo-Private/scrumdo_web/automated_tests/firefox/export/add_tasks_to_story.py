# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re
from scrumdo_web.automated_tests.selenium.functional_test_case import FunctionalTestCase

class AddTasksToStory(FunctionalTestCase):
    def test_28_add_tasks_to_story(self):
        driver = self.driver
        self.login()
        driver.find_element_by_css_selector("h1").click()
        driver.find_element_by_link_text("TestOrg").click()
        driver.find_element_by_link_text("Projects").click()
        driver.get(self.base_url + "/projects/project/testproject/")
        driver.find_element_by_link_text("TestProject").click()
        driver.find_element_by_link_text("Story List").click()
        driver.find_element_by_link_text("0 Tasks").click()
        for i in range(60):
            try:
                if self.is_element_present(By.CSS_SELECTOR, "input.task_summary_input"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        driver.find_element_by_css_selector("input[name=\"summary\"]").clear()
        driver.find_element_by_css_selector("input[name=\"summary\"]").send_keys("test task")
        driver.find_element_by_css_selector("input.button.blue").click()
        driver.find_element_by_link_text("TestProject").click()
        driver.find_element_by_link_text("Story List").click()
        self.assertEquals('1 Tasks' in driver.find_element(By.TAG_NAME,'body').text, True)

if __name__ == "__main__":
    unittest.main()
