# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re
from scrumdo_web.automated_tests.selenium.functional_test_case import FunctionalTestCase

class ModifyStoryRanking(FunctionalTestCase):
    def test_25_modify_story_ranking(self):
        driver = self.driver
        mouse = self.mouse
        self.login()
        driver.find_element_by_css_selector("h1").click()
        driver.find_element_by_link_text("TestOrg").click()
        driver.find_element_by_link_text("Projects").click()
        driver.get(self.base_url + "/projects/project/testproject/")
        driver.find_element_by_link_text("TestProject").click()
        driver.find_element_by_link_text("Story List").click()
        element = driver.find_element_by_xpath('//*[@id="story_1"]')
        mouse.drag_and_drop_by_offset(element, 100, 0)

if __name__ == "__main__":
    unittest.main()
