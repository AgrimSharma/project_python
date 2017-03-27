# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re
from scrumdo_web.automated_tests.selenium.functional_test_case import FunctionalTestCase

class AccountTests(FunctionalTestCase):
    def test_6_create_account_for_new_users(self):
        driver = self.driver
        #driver.get(self.base_url + "/")
        driver.get(self.base_url + "/account/signup/")
        driver.find_element_by_id("id_username").clear()
        driver.find_element_by_id("id_username").send_keys("testuser")
        driver.find_element_by_id("id_password1").clear()
        driver.find_element_by_id("id_password1").send_keys("testuserpassword")
        driver.find_element_by_id("id_password2").clear()
        driver.find_element_by_id("id_password2").send_keys("testuserpassword")
        driver.find_element_by_id("id_email").clear()
        driver.find_element_by_id("id_email").send_keys("andriicorporate@gmail.com")
        driver.find_element_by_xpath("//input[@value='Create Account »']").click()
        self.assertTrue('Confirmation email sent' in driver.find_element(By.TAG_NAME,'body').text)

if __name__ == "__main__":
    unittest.main()
