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

class TeamTests(TEST_CASE_CLASS):
    def test_13_create_a_team(self):
        driver = self.login()
        driver.get(self.base_url + "/organization/testorgbetatest/teams")
        driver.find_element_by_link_text("New Team").click()
        driver.find_element_by_id("id_name").click()
        driver.find_element_by_id("id_name").clear()
        driver.find_element_by_id("id_name").send_keys("ATestTeam")
        Select(driver.find_element_by_id("id_access_type")).select_by_visible_text("Read / Write")
        driver.find_element_by_css_selector("button.primaryAction").click()
        #check that the team has been created
        driver.get(self.base_url + "/organization/testorgbetatest/teams")
        self.assertTrue('ATestTeam' in driver.find_element(By.TAG_NAME,'body').text)
        #self.assertEquals('Team Created.' in driver.find_element(By.TAG_NAME,'body').text, True)

    def test_14_delete_team(self):
        driver = self.login()
        driver.get(self.base_url + "/organization/testorgbetatest/teams")
        driver.find_element_by_id("delete_button").click()
        time.sleep(1)
        alert = driver.switch_to_alert()
        alert.accept()
        #check that the team has been successfully deleted
        driver.get(self.base_url + "/organization/testorgbetatest/teams")
        self.assertFalse('ATestTeam' in driver.find_element(By.TAG_NAME,'body').text)

    def test_15_add_users_to_team(self):
        driver = self.login()
        driver.get(self.base_url + "/organization/testorgbetatest/teams")
        driver.find_element_by_name("invitee").clear()
        driver.find_element_by_name("invitee").send_keys("scrumdoselenium")
        driver.find_element_by_css_selector("input.button.green").click()
        driver.find_element_by_link_text("TestOrgBetaTest").click()
        driver.find_element_by_link_text("Teams").click()
        self.assertTrue('Members (1 members)' in driver.find_element(By.ID,'team_1').text)

if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(TeamTests("test_13_create_a_team"))
    suite.addTest(TeamTests("test_14_delete_team"))
    suite.addTest(TeamTests("test_15_add_users_to_team"))
    result = unittest.TextTestRunner(buffer=True,verbosity=2,resultclass=ScrumDoTestResult).run(suite)


