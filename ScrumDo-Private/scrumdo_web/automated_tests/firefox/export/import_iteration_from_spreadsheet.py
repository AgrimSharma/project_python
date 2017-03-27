# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re
from scrumdo_web.automated_tests.selenium.functional_test_case import FunctionalTestCase

class ImportIterationFromSpreadsheet(FunctionalTestCase):
    def test_35_import_iteration_from_spreadsheet(self):
        driver = self.driver
        self.login()
        driver.get(self.base_url + "/projects/project/testproject/")
        driver.find_element_by_link_text("TestProject").click()
        driver.find_element_by_link_text("Import Iteration").click()
        for i in range(60):
            try:
                if self.is_element_present(By.XPATH, "(//form[@action= '/projects/project/testproject/iteration/2/import']//input[@id='id_import_file'])"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        #driver.find_element_by_xpath("(//form[@action= '/projects/project/testproject/iteration/2/import']//input[@id='id_import_file'])").clear()
        driver.find_element_by_xpath("(//form[@action= '/projects/project/testproject/iteration/2/import']//input[@id='id_import_file'])").send_keys("/home/andrii/venv/scrumdo/website/new_iteration.xls")
        driver.find_element_by_xpath("(//form[@action= '/projects/project/testproject/iteration/2/import']//button)").click()
        driver.get(self.base_url + "/projects/project/testproject/iteration/2")
        try: self.assertEqual("6", driver.find_element_by_xpath("//div[@id='iteration_stats']/div/h4").text)
        except AssertionError as e: self.verificationErrors.append(str(e))


if __name__ == "__main__":
    unittest.main()
