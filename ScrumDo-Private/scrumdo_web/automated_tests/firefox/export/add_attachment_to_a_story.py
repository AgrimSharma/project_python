# -*- coding: utf-8 -*-
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re
from scrumdo_web.automated_tests.selenium.functional_test_case import FunctionalTestCase

class AddAttachmentToAStory(FunctionalTestCase):
    def test_24_add_attachment_to_a_story(self):
        driver = self.driver
        self.login()
        #driver.find_element_by_css_selector("h1").click()
        #driver.find_element_by_link_text("TestOrg").click()
        #driver.find_element_by_link_text("Projects").click()
        #driver.get(self.base_url + "/projects/project/testproject/")
        #driver.find_element_by_link_text("TestProject").click()
        #driver.find_element_by_link_text("Story List").click()
        driver.get(self.base_url + "/projects/project/testproject/iteration/1")
        driver.find_element_by_css_selector("a[title=\"Attach a file\"] > img").click()
        for i in range(60):
            try:
                if self.is_element_present(By.ID, "id_attachment_file-2"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        driver.find_element_by_id("id_attachment_file-2").send_keys("%s/story_attachment.txt" % os.getcwd())
        driver.find_element_by_id("upload_button-2").click()
        self.assertTrue('story_attachment' in driver.find_element(By.TAG_NAME,'body').text)

if __name__ == "__main__":
    unittest.main()
