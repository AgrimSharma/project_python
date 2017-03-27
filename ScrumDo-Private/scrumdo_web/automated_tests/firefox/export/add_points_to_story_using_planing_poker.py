# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re
from scrumdo_web.automated_tests.selenium.functional_test_case import FunctionalTestCase

class AddPointsToStoryUsingPlaningPoker(FunctionalTestCase):
    def test_31_add_points_to_story_using_planing_poker(self):
        driver = self.driver
        self.login()
        driver.get(self.base_url + "/poker/play/testproject")
        driver.find_element_by_link_text("Become Scrum Master").click()
        time.sleep(1)
        alert = driver.switch_to_alert()
        alert.accept()
        #for i in range(60):
        #    try:
        #        if self.is_element_present(By.XPATH, "//a[contains(@href, '/projects/story/1')]"): break
        #    except: pass
        #    time.sleep(1)
        #else: self.fail("time out")
        driver.execute_script("window.scrollTo(0,300);")
        driver.find_element_by_xpath("//a[contains(@href, '/projects/story/1')]").click()
        for i in range(60):
            try:
                if self.is_element_present(By.XPATH, "//a[contains(text(),'5')][2]"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        driver.find_element_by_xpath("//a[contains(text(),'5')][2]").click()
        driver.find_element_by_link_text("Save").click()
        driver.get(self.base_url + "/projects/project/testproject/iteration/1")
        try: self.assertEqual("5", driver.find_element_by_css_selector("li#story_1.story_block div.pointsBox").text)
        except AssertionError as e: self.verificationErrors.append(str(e))

if __name__ == "__main__":
    unittest.main()
