# -*- coding: utf-8 -*-
import time
from django.conf import settings
from django.utils import unittest
from functional_test_case import  *
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select, WebDriverWait
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

class AccountTests(TEST_CASE_CLASS):
    def test_create_a_new_organization(self):
        driver = self.login()
        driver = self.create_organization(name="Create Org", subscription=False)
        self.assertTrue('Choose a subscription plan for Create Org.' in driver.find_element(By.TAG_NAME,'body').text)

    def test_6_create_account_for_new_users(self):
        driver = self.driver
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
        self.assertTrue('Create an Organization and a Project' in driver.find_element(By.TAG_NAME,'body').text)

    def test_7_create_a_new_organization_subscription(self):
        driver = self.login()
        driver = self.create_organization(name="TestOrgBetaTest", subscription=True)
        self.assertTrue('TestOrgBetaTest Projects' in driver.find_element(By.TAG_NAME,'body').text)

    def test_8_update_organization(self):
        driver = self.login()
        driver.get(self.base_url + "/organization/testorgbetatest/edit")
        driver.find_element_by_id("id_description").clear()
        driver.find_element_by_id("id_description").send_keys("This is a testing organization")
        driver.find_element_by_css_selector("button.primaryAction").click()
        self.assertTrue('Organization Updated' in driver.find_element(By.TAG_NAME,'body').text)

    def test_40_add_message_to_scrumlog(self):
        driver = self.login()
        driver = self.create_project(name="ScrumLog")
        driver.get(self.base_url + "/projects/project/scrumlog/")
        driver.execute_script("window.scrollTo(0,350);")
        driver.find_element_by_css_selector("a#view_scrum_log_link").click()
        driver.find_element_by_xpath("//textarea[@id='id_message']").clear()
        driver.find_element_by_xpath("//textarea[@id='id_message']").send_keys("Test 40 add message to scrumlog")
        Select(driver.find_element_by_xpath("//select[@id='id_related']")).select_by_visible_text("Backlog")
        driver.find_element_by_xpath("//form[@id='scrum_log_form']/fieldset/div[4]/div/button").click()
        for i in range(30):
            try:
                if self.is_element_present(By.XPATH, "//div[@id='log_1']/div[2]/p"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out: no element present under \"%s\" xpath!")
        self.assertTrue("Test 40 add message to scrumlog" in
                        driver.find_element_by_xpath("//div[@id='log_1']/div[2]/p").text)

    def test_41_switch_organization(self):
        driver = self.login()
        driver = self.create_organization(name="SwitchOrg", subscription=True)
        self.assertTrue("SwitchOrg" in driver.find_element_by_xpath("//div[@id='organization-body-holder']/h1").text)
        driver.find_element_by_link_text("SwitchOrg").click()
        driver.find_element_by_link_text("Switch Organization").click()
        driver.find_element_by_xpath("//a[contains(@href, '/organization/testorgbetatest/dashboard')]").click()
        self.assertTrue("TestOrgBetaTest" in driver.find_element_by_xpath("//div[@id='organization-body-holder']/h1").text)

if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(AccountTests("test_6_create_account_for_new_users"))
    suite.addTest(AccountTests("test_7_create_a_new_organization_subscription"))
    suite.addTest(AccountTests("test_8_update_organization"))
    suite.addTest(AccountTests("test_40_add_message_to_scrumlog"))
    suite.addTest(AccountTests("test_41_switch_organization"))
    result = unittest.TextTestRunner(buffer=True,verbosity=2,resultclass=ScrumDoTestResult).run(suite)

