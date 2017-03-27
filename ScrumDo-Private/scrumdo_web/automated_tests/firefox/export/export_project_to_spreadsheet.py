# -*- coding: utf-8 -*-
import os
import filecmp
from django.conf import settings
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re
from scrumdo_web.automated_tests.selenium.functional_test_case import FunctionalTestCase

class ExportProjectToSpreadsheet(FunctionalTestCase):
    def test_33_export_project_to_spreadsheet(self):
        driver = self.driver
        self.login()
        #remove last exported file if exists
        if os.path.exists("%s/automated_tests/results/project.xls" % settings.PROJECT_ROOT):
            os.unlink("%s/automated_tests/results/project.xls" % settings.PROJECT_ROOT)
        driver.get(self.base_url + "/projects/project/testproject/")
        driver.find_element_by_link_text("TestProject").click()
        driver.find_element_by_link_text("Export Project").click()
        #for i in range(60):
        #    try:
        #        if self.is_element_present(By.XPATH, "(//form[@action= '/projects/project/testproject/export']//button)"): break
        #    except: pass
        #    time.sleep(1)
        #else: self.fail("time out")
        driver.find_element_by_xpath("(//form[@action= '/projects/project/testproject/export']//button)").click()

        #compare if newly exported file equals with expected one
        for i in range(30):
            try:
                success_export = filecmp.cmp(
                    "%s/automated_tests/results/project.xls" % settings.PROJECT_ROOT,
                    "%s/automated_tests/results/expected/project.xls" % settings.PROJECT_ROOT
                )
                break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        self.assertTrue(success_export)

if __name__ == "__main__":
    unittest.main()
