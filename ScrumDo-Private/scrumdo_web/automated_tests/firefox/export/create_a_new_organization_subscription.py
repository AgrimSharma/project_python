# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re
from scrumdo_web.automated_tests.selenium.functional_test_case import FunctionalTestCase

class CreateANewOrganizationSubscription(FunctionalTestCase):
    def test_7_create_a_new_organization_subscription(self):
        driver = self.driver
        self.login()
        driver.find_element_by_link_text("Create New Organization").click()
        driver.find_element_by_id("id_name").clear()
        driver.find_element_by_id("id_name").send_keys("TestOrg")
        driver.find_element_by_css_selector("button.primaryAction").click()

        driver.execute_script("window.scrollTo(0,document.body.scrollHeight/2);")
        #driver.get(self.base_url + "/subscription/testorg")
        driver.find_elements_by_css_selector("table.subscription_table td.subscribe_button_cell a.button.green.small")[0].click()
        #subsbtn = driver.find_elements(By.CSS_SELECTOR, "table.subscription_table td.subscribe_button_cell a.button.green.small")
        #driver.get(subsbtn[0].get_attribute('href'))
        #driver.find_element_by_css_selector('table.subscription_table td.subscribe_button_cell a.button.green.small').click()
        #self.mouse.click(self.driver.find_elements_by_css_selector("table.subscription_table td.subscribe_button_cell a.button.green.small")[0]).perform()


        driver.find_element_by_id("credit_card_first_name").clear()
        driver.find_element_by_id("credit_card_first_name").send_keys("Scrum")
        driver.find_element_by_id("credit_card_last_name").clear()
        driver.find_element_by_id("credit_card_last_name").send_keys("Do")
        driver.find_element_by_id("credit_card_number").clear()
        driver.find_element_by_id("credit_card_number").send_keys("4222222222222")
        driver.find_element_by_id("credit_card_verification_value").clear()
        driver.find_element_by_id("credit_card_verification_value").send_keys("343")
        Select(driver.find_element_by_id("credit_card_month")).select_by_visible_text("7 - July")
        Select(driver.find_element_by_id("credit_card_year")).select_by_visible_text("2014")
        driver.find_element_by_name("purchase_button").click()
        driver.find_element_by_link_text("Continue...").click()
        self.assertTrue('TestOrg Projects' in driver.find_element(By.TAG_NAME,'body').text)

if __name__ == "__main__":
    unittest.main()
