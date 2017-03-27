# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re
from scrumdo_web.automated_tests.selenium.functional_test_case import FunctionalTestCase

class DeleteTeam(FunctionalTestCase):
    def test_14_delete_team(self):
        driver = self.driver
        self.login()
        driver.find_element_by_css_selector("div.organization_picker > a").click()
        driver.find_element_by_link_text("TestOrg").click()
        driver.find_element_by_link_text("Teams").click()
        for i in range(60):
            try:
                if self.is_element_present(By.ID, "delete_button"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        driver.find_element_by_id("delete_button").click()
        time.sleep(1)
        alert = driver.switch_to_alert()
        alert.accept()
        driver.get(self.base_url + "/organization/testorg/teams")
        self.assertEquals('ATestTeam' in driver.find_element(By.TAG_NAME,'body').text, False)

if __name__ == "__main__":
    unittest.main()
