# -*- coding: utf-8 -*-
import os, sys, time
import filecmp, requests
from django.conf import settings
from django.utils import unittest
from functional_test_case import  *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC

try:
    # defines which webdriver to use for testing
    exec 'from functional_test_case import %s as TEST_CASE_CLASS' % os.environ['TEST_CASE_CLASS']
except KeyError:
    print '"TEST_CASE_CLASS" environment variable not found, to '\
          'locally "export TEST_CASE_CLASS=FunctionalTestCase", '\
          'with sauce "export TEST_CASE_CLASS=Selenium2OnSauce".'
    sys.exit()
except ImportError:
    print "Can't import '%s'" % os.environ['TEST_CASE_CLASS']
    sys.exit()


class ExcelTests(TEST_CASE_CLASS):
    """ Each data exporting test should follow
    with into the common list of steps abstraction
        0. common data importing prerequsity test has to beinitially fired.
        1. now a test can follow to pass all the set of instructions with in
        2. finally we can download the file in background to compare and diff
    - do assertion checks
    """
    def test_35_import_iteration_from_spreadsheet(self):
        driver = self.login()
        #driver.find_element_by_xpath("//a[contains(@href, '/organization/testorgbetatest/dashboard')]").click()
        driver = self.create_project(name="TestProjectExcel")

        driver.get(self.base_url + "/projects/project/testprojectexcel/")
        driver.find_element_by_link_text("TestProjectExcel").click()
        driver.find_element_by_link_text("Import Iteration").click()
        for i in range(30):
            try:
                if self.is_element_present(By.XPATH, "(//form[@action= '/projects/project/testprojectexcel/iteration/2/import']//input[@id='id_import_file'])"):
                    break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        driver.find_element_by_xpath("(//form[@action= '/projects/project/testprojectexcel/iteration/2/import']//input[@id='id_import_file'])")\
              .send_keys("%s/automated_tests/iteration_to_import.xls" % settings.PROJECT_ROOT)
        driver.find_element_by_xpath("(//form[@action= '/projects/project/testprojectexcel/iteration/2/import']//button)").click()
        driver.get(self.base_url + "/projects/project/testprojectexcel/iteration/2")
        try: self.assertEqual("5", driver.find_element_by_xpath("//div[@id='iteration_stats']/div/h4").text)
        except AssertionError as e: self.verificationErrors.append(str(e))

    def test_34_export_iteration_to_spreadsheet(self):
        driver = self.login()
        driver.get(self.base_url + "/projects/project/testprojectexcel/iteration/2")
        driver.find_element_by_link_text("TestProjectExcel").click()
        driver.find_element_by_link_text("Export Iteration").click()
        driver.find_element_by_xpath("(//form[@action= '/projects/project/testprojectexcel/iteration/2/export']//button)").click()

        try:
            dwnlnk = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "Download File")))
            """ This waits up to 10 seconds before throwing a TimeoutException or if it finds the element will return it in 0 - 10 seconds.
                WebDriverWait by default calls the ExpectedCondition every 500 milliseconds until it returns successfully.
                A successful return is for ExpectedCondition type is Boolean return true or not null return value for all other ExpectedCondition types """
        except TimeoutException as e: self.verificationErrors.append(str(e))
        finally:
            cookies = {}
            for cookie in driver.get_cookies():
                cookies[cookie['name']]=cookie['value']
            url = dwnlnk.get_attribute('href')
            res = requests.get(url, cookies=cookies)
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.headers['content-type'], 'application/vnd.ms-excel')
            export_result = "%s/automated_tests/results/iteration.xls" % settings.PROJECT_ROOT
            expected_result = "%s/automated_tests/results/expected/iteration.xls" % settings.PROJECT_ROOT
            if os.path.exists(export_result): os.unlink(export_result)
            f = open(export_result, 'w'); f.write(res.content); f.close()
            self.assertTrue(filecmp.cmp(export_result,expected_result))

    def test_33_export_project_to_spreadsheet(self):
        driver = self.login()
        driver.get(self.base_url + "/projects/project/testprojectexcel/")
        driver.find_element_by_link_text("TestProjectExcel").click()
        driver.find_element_by_link_text("Export Project").click()
        driver.find_element_by_xpath("(//form[@action= '/projects/project/testprojectexcel/export']//button)").click()

        try:
            dwnlnk = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "Download File")))
            """ This waits up to 10 seconds before throwing a TimeoutException or if it finds the element will return it in 0 - 10 seconds.
                WebDriverWait by default calls the ExpectedCondition every 500 milliseconds until it returns successfully.
                A successful return is for ExpectedCondition type is Boolean return true or not null return value for all other ExpectedCondition types """
        except TimeoutException as e: self.verificationErrors.append(str(e))
        finally:
            cookies = {}
            for cookie in driver.get_cookies():
                cookies[cookie['name']]=cookie['value']
            url = dwnlnk.get_attribute('href')
            res = requests.get(url, cookies=cookies)
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.headers['content-type'], 'application/vnd.ms-excel')
            export_result = "%s/automated_tests/results/project.xls" % settings.PROJECT_ROOT
            expected_result = "%s/automated_tests/results/expected/project.xls" % settings.PROJECT_ROOT
            if os.path.exists(export_result): os.unlink(export_result)
            f = open(export_result, 'w'); f.write(res.content); f.close()
            self.assertTrue(filecmp.cmp(export_result,expected_result))


    def test_16_organization_data_export_to_excel(self):
        driver = self.login()
        driver.get(self.base_url + "/projects/project/testprojectexcel/")
        driver.find_element_by_link_text("TestOrgBetaTest").click()
        driver.find_element_by_link_text("Export").click()
        driver.find_element_by_css_selector("input.button.blue").click()

        try:
            dwnlnk = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "Download File")))
            """ This waits up to 10 seconds before throwing a TimeoutException or if it finds the element will return it in 0 - 10 seconds.
                WebDriverWait by default calls the ExpectedCondition every 500 milliseconds until it returns successfully.
                A successful return is for ExpectedCondition type is Boolean return true or not null return value for all other ExpectedCondition types """
        except TimeoutException as e: self.verificationErrors.append(str(e))
        finally:
            cookies = {}
            for cookie in driver.get_cookies():
                cookies[cookie['name']]=cookie['value']
            url = dwnlnk.get_attribute('href')
            res = requests.get(url, cookies=cookies)
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.headers['content-type'], 'application/vnd.ms-excel')
            export_result = "%s/automated_tests/results/organization.xls" % settings.PROJECT_ROOT
            expected_result = "%s/automated_tests/results/expected/organization.xls" % settings.PROJECT_ROOT
            if os.path.exists(export_result): os.unlink(export_result)
            f = open(export_result, 'w'); f.write(res.content); f.close()
            self.assertTrue(filecmp.cmp(export_result,expected_result))


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(ExcelTests("test_35_import_iteration_from_spreadsheet"))
    suite.addTest(ExcelTests("test_34_export_iteration_to_spreadsheet"))
    suite.addTest(ExcelTests("test_33_export_project_to_spreadsheet"))
    suite.addTest(ExcelTests("test_16_organization_data_export_to_excel"))
    result = unittest.TextTestRunner(buffer=True,verbosity=2,resultclass=ScrumDoTestResult).run(suite)

