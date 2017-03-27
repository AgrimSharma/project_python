# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import unittest, time, re
from scrumdo_web.automated_tests.selenium.functional_test_case import FunctionalTestCase

class AddStoriesToIteration(FunctionalTestCase):
    def test_43_add_stories_to_iteration(self):
        driver = self.driver
        self.login()
        driver.get(self.base_url + "/projects/project/testproject/stories/")
        Select(driver.find_element_by_id("iterationChooser")).select_by_visible_text("TestIteration")
        element = driver.find_element_by_css_selector("#backlog_div li#story_2")
        target =  driver.find_element_by_css_selector("#story_div ul#iteration_column")
        ActionChains(driver).drag_and_drop(element, target).perform()
        driver.get(self.base_url + "/projects/project/testproject/iteration/3")
        driver.find_element_by_link_text("TestProject").click()
        driver.find_element_by_css_selector("ul.project-menu-iteration-list li.project-menu-current-iteration a").click()
        self.assertTrue('#2' in driver.find_element(By.TAG_NAME,'body').text)


if __name__ == "__main__":
    unittest.main()
