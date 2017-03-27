# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re
from scrumdo_web.automated_tests.selenium.functional_test_case import FunctionalTestCase

class UpdateStoryPoints(FunctionalTestCase):
    def test_32_update_story_points(self):
        driver = self.driver
        self.login()
        driver.get(self.base_url + "/projects/project/testproject/iteration/1")
        driver.find_element_by_css_selector("#story_2 a.edit-story-button > img").click()
        for i in range(60):
            try:
                if self.is_element_present(By.XPATH, "(//input[@id='id_points_6'])[2]"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        driver.find_element_by_xpath("(//input[@id='id_points_6'])[2]").click()
        driver.find_element_by_xpath("//input[@value='Update Story']").click()
        driver.get(self.base_url + "/projects/project/testproject/iteration/1")
        try: self.assertEqual("5", driver.find_element_by_css_selector("li#story_2.story_block div.pointsBox").text)
        except AssertionError as e: self.verificationErrors.append(str(e))


if __name__ == "__main__":
    unittest.main()
