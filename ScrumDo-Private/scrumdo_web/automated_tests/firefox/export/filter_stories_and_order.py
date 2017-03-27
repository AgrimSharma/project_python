# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re
from scrumdo_web.automated_tests.selenium.functional_test_case import FunctionalTestCase

class FilterStoriesOrderVariousCriteria(FunctionalTestCase):
    def test_37_filter_stories_order_various_criteria(self):
        driver = self.driver
        self.login()
        driver.get(self.base_url + "/projects/project/testproject/iteration/2")
        driver.execute_script("window.scrollTo(0,350);")
        driver.find_element_by_xpath("//a[contains(@href, '#filterDialog')]").click()
        Select(driver.find_element_by_xpath("//select[@name='status']")).select_by_visible_text("Todo")
        driver.execute_script("window.scrollTo(0,350);")
        driver.find_element_by_xpath("(//input[@name='order_by'])[2]").click()
        driver.find_element_by_xpath("//input[@id='filter_button']").click()
        time.sleep(2)
        self.assertTrue('#2' in driver.find_elements_by_css_selector("ul#story_list.iteration_story_list li")[0].text)


if __name__ == "__main__":
    unittest.main()
