# -*- coding: utf-8 -*-
import time
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

class EpicTests(TEST_CASE_CLASS):
    def test_17_create_epic(self):
        driver = self.login()
        driver.get(self.base_url + "/projects/project/testproject/")
        driver.find_element_by_link_text("TestProject").click()
        driver.find_element_by_link_text("Epics").click()
        driver.find_element_by_link_text("New Epic").click()
        points = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'id_points')))
        points.clear(); points.send_keys("12")
        driver.execute_script("$('#id_summary').val('test epic')")
        driver.find_element_by_css_selector("button.primaryAction").click()
        try: WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "#E1")))
        except TimeoutException as e: self.verificationErrors.append(str(e))

    def test_18_update_epic(self):
        driver = self.login()
        driver.get(self.base_url + "/projects/project/testproject/epics")
        driver.find_element_by_css_selector("span.epic_edit img").click()
        summary = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'id_summary')))
        summary.clear(); summary.send_keys("test epic updated")
        driver.find_element_by_css_selector("button.primaryAction").click()

        try: WebDriverWait(driver, 10).until(
                lambda x: "test epic updated" in
                          x.find_element(By.CSS_SELECTOR, ".epic_text").text)
        except TimeoutException as e: self.verificationErrors.append(str(e))

    def test_19_delete_epic(self):
        driver = self.login()
        driver.get(self.base_url + "/projects/project/testproject/epics")
        driver.find_element_by_css_selector("span.epic_edit img").click()
        try: WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input.button.red"))).click()
        except TimeoutException as e: self.verificationErrors.append(str(e))
        finally: alert = driver.switch_to_alert(); alert.accept(); driver.switch_to_active_element()
        WebDriverWait(driver, 10).until_not(lambda x: x.find_elements(By.CLASS_NAME, "epic_list_item"))
        self.assertListEqual(driver.find_elements(By.CLASS_NAME, "epic_list_item"), [])

if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(EpicTests("test_17_create_epic"))
    suite.addTest(EpicTests("test_18_update_epic"))
    suite.addTest(EpicTests("test_19_delete_epic"))
    result = unittest.TextTestRunner(buffer=True,verbosity=2,resultclass=ScrumDoTestResult).run(suite)


