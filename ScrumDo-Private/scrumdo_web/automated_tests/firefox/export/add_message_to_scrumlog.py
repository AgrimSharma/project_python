# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re
from scrumdo_web.automated_tests.selenium.functional_test_case import FunctionalTestCase

class AddMessageToScrumlog(FunctionalTestCase):
    def test_40_add_message_to_scrumlog(self):
        driver = self.driver
        self.login()
        driver.get(self.base_url + "/projects/project/testproject/")
        driver.execute_script("window.scrollTo(0,800);")
        driver.find_element_by_css_selector("a#view_scrum_log_link").click()
        driver.find_element_by_xpath("//textarea[@id='id_message']").clear()
        driver.find_element_by_xpath("//textarea[@id='id_message']").send_keys("Test message")
        Select(driver.find_element_by_xpath("//select[@id='id_related']")).select_by_visible_text("TestIteration")
        driver.find_element_by_xpath("//form[@id='scrum_log_form']/fieldset/div[4]/div/button").click()
        for i in range(60):
            try:
                if self.is_element_present(By.XPATH, "//div[@id='log_1']/div[2]/p"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        try: self.assertEqual("Test message", driver.find_element_by_xpath("//div[@id='log_1']/div[2]/p").text)
        except AssertionError as e: self.verificationErrors.append(str(e))

if __name__ == "__main__":
    unittest.main()
