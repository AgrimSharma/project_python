# -*- coding: utf-8 -*-
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

class ProjectTests(TEST_CASE_CLASS):
    def test_9_create_a_project(self):
        driver = self.login()
        driver = self.create_project(name="TestProject")
        self.assertEquals('Project Created' in driver.find_element(By.TAG_NAME,'body').text, True)

    def test_10_update_project_settings(self):
        driver = self.login()
        driver.get(self.base_url + "/projects/project/testproject/")
        driver.find_element_by_link_text("TestProject").click()
        driver.find_element_by_link_text("Project Admin").click()
        driver.find_element_by_id("id_description").clear()
        driver.find_element_by_id("id_description").send_keys("this is a test project")
        driver.find_element_by_css_selector("#tabs-1 button.primaryAction").click()
        self.assertTrue('Project options Saved.' in driver.find_element(By.TAG_NAME,'body').text)

    def test_11_delete_project(self):
        driver = self.login()
        driver.get(self.base_url + "/projects/project/testprojectexcel/admin")
        driver.find_element_by_link_text("Admin").click()
        driver.find_element_by_link_text("Delete project").click()
        driver.find_element_by_css_selector("#delete_project_form > input[type=\"submit\"]").click()
        self.assertEquals('Project TestProjectExcel deleted.' in driver.find_element(By.TAG_NAME,'body').text, True)

    def test_12_archive_project(self):
        driver = self.login()
        driver = self.create_project(name="TestProjectArchive")
        driver.get(self.base_url + "/projects/project/testprojectarchive/admin")
        driver.find_element_by_link_text("Admin").click()
        driver.find_element_by_id("archiveFormButton").click()
        self.assertTrue('This project is archived.' in driver.find_element(By.TAG_NAME,'body').text)

if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(ProjectTests("test_9_create_a_project"))
    suite.addTest(ProjectTests("test_10_update_project_settings"))
    suite.addTest(ProjectTests("test_11_delete_project"))
    suite.addTest(ProjectTests("test_12_archive_project"))
    result = unittest.TextTestRunner(buffer=True,verbosity=2,resultclass=ScrumDoTestResult).run(suite)
