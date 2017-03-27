# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re

class AddUsersToTeam(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30)
        self.base_url = "http://localhost:9000"
        self.verificationErrors = []
    
    def test_15_add_users_to_team(self):
        driver = self.driver
        driver.get(self.base_url + "/account/login")
        driver.find_element_by_id("id_username").clear()
        driver.find_element_by_id("id_username").send_keys("scrumdoselenium")
        driver.find_element_by_id("id_password").clear()
        driver.find_element_by_id("id_password").send_keys("scrumdotesting")
        driver.find_element_by_xpath("//input[@value='Log In »']").click()
        driver.find_element_by_css_selector("div.organization_picker > a").click()
        driver.find_element_by_link_text("TestOrg").click()
        driver.find_element_by_link_text("Teams").click()
        driver.find_element_by_name("invitee").clear()
        driver.find_element_by_name("invitee").send_keys("scrumdoselenium")
        driver.find_element_by_css_selector("input.button.green").click()
        driver.find_element_by_link_text("TestOrg").click()
        driver.find_element_by_link_text("Teams").click()
        self.assertEquals('Members (1 members)' in driver.find_element(By.TAG_NAME,'body').text, True)
    
    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException, e: return False
        return True
    
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
