# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import unittest, time, re
from scrumdo_web.automated_tests.selenium.functional_test_case import FunctionalTestCase

class UpdateTasksOfStory(FunctionalTestCase):
    def test_29_update_tasks_of_story(self):
        driver = self.driver
        mouse = self.mouse
        self.login()
        driver.find_element_by_css_selector("h1").click()
        driver.find_element_by_link_text("TestOrg").click()
        driver.find_element_by_link_text("Projects").click()
        driver.get(self.base_url + "/projects/project/testproject/")
        driver.find_element_by_link_text("TestProject").click()
        driver.find_element_by_link_text("Story List").click()
        driver.find_element_by_link_text("1 Tasks").click()
        for i in range(60):
            try:
                if self.is_element_present(By.LINK_TEXT, "test task"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        element = driver.find_element_by_link_text('test task')
        mouse.move_to_element(element).perform()
        for i in range(60):
            try:
                if self.is_element_present(By.LINK_TEXT, "Edit"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        driver.find_element_by_link_text("Edit").click()
        for i in range(60):
            try:
                if self.is_element_present(By.XPATH, "//input[@id='id_summary']"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        driver.find_element_by_xpath("//input[@id='id_summary']").clear()
        driver.find_element_by_xpath("//input[@id='id_summary']").send_keys("test task updated")
        driver.find_element_by_css_selector("#edit_task_1 > input.button").click()
        driver.find_element_by_link_text("TestProject").click()
        driver.find_element_by_link_text("Story List").click()
        driver.find_element_by_link_text("1 Tasks").click()
        for i in range(60):
            try:
                if self.is_element_present(By.LINK_TEXT, "test task updated"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        self.assertEquals('test task updated' in driver.find_element(By.TAG_NAME,'body').text, True)

if __name__ == "__main__":
    unittest.main()
