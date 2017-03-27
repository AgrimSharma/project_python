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

class ExportIterationToSpreadsheet(FunctionalTestCase):
    def test_34_export_iteration_to_spreadsheet(self):
        driver = self.driver
        self.login()
        if os.path.exists("%s/automated_tests/results/iteration.xls" % settings.PROJECT_ROOT):
            os.unlink("%s/automated_tests/results/iteration.xls" % settings.PROJECT_ROOT)
        driver.get(self.base_url + "/projects/project/testproject/iteration/2")
        driver.find_element_by_link_text("TestProject").click()
        driver.find_element_by_link_text("Export Iteration").click()
        driver.find_element_by_xpath("(//form[@action= '/projects/project/testproject/iteration/2/export']//button)").click()

        #compare if newly exported file equals with expected one
        for i in range(30):
            try:
                success_export = filecmp.cmp(
                    "%s/automated_tests/results/iteration.xls" % settings.PROJECT_ROOT,
                    "%s/automated_tests/results/expected/iteration.xls" % settings.PROJECT_ROOT
                )
                break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        self.assertTrue(success_export)





if __name__ == "__main__":
    unittest.main()
