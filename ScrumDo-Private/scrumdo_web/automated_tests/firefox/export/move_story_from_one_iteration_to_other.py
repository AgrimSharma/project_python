# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re
from scrumdo_web.automated_tests.selenium.functional_test_case import FunctionalTestCase

class MoveStoryFromOneIterationToOther(FunctionalTestCase):
    def test_38_move_story_from_one_iteration_to_other(self):
        driver = self.driver
        self.login()
        driver.get(self.base_url + "/projects/project/testproject/iteration_create")
        driver.find_element_by_id("id_name").clear()
        driver.find_element_by_id("id_name").send_keys("Iteration #2")
        driver.find_element_by_id("id_start_date").click()
        driver.find_element_by_link_text("1").click()
        driver.find_element_by_id("id_end_date").click()
        driver.find_element_by_link_text("31").click()
        driver.find_element_by_xpath("//button[@type='submit']").click()
        driver.get(self.base_url + "/projects/project/testproject/stories/")
        Select(driver.find_element_by_xpath("//select[@id='iterationChooser']")).select_by_visible_text("Iteration #2")
        Select(driver.find_element_by_xpath("//select[@id='backlogChooser']")).select_by_visible_text("TestIteration")
        time.sleep(2)
        element = driver.find_element_by_css_selector("#backlog_div li#story_3")
        target =  driver.find_element_by_css_selector("#story_div ul#iteration_column")
        ActionChains(driver).drag_and_drop(element, target).perform()
        #time.sleep(2)
        #element = driver.find_element_by_css_selector("#backlog_div li#story_5")
        #target =  driver.find_element_by_css_selector("#story_div ul#iteration_column")
        #ActionChains(driver).drag_and_drop(element, target).perform()
        #time.sleep(2)
        #element = driver.find_element_by_css_selector("#backlog_div li#story_7")
        #target =  driver.find_element_by_css_selector("#story_div ul#iteration_column")
        #ActionChains(driver).drag_and_drop(element, target).perform()
        driver.get(self.base_url + "/projects/project/testproject/iteration/3")

        self.assertTrue('#3' in driver.find_element(By.TAG_NAME,'body').text)


if __name__ == "__main__":
    unittest.main()
