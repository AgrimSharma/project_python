# -*- coding: utf-8 -*-
import os, sys, time
from django.conf import settings
from django.utils import unittest
from functional_test_case import  *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC

try:
    # defines which webdriver and test results class to use for the testing session
    import_super_test = 'from functional_test_case import %s as TEST_CASE_CLASS'
    import_result_cls = 'from functional_test_case import %s as TEST_RESULT_CLASS'
    exec import_super_test % os.environ['TEST_CASE_CLASS']
    if os.environ['TEST_CASE_CLASS'] == 'FunctionalTestCase':
        exec import_result_cls % 'ScrumDoTestResult'
    else: exec import_result_cls % 'SauceTestResult'
except KeyError:
    print '"TEST_CASE_CLASS" environment variable not found, to '  \
          'locally "export TEST_CASE_CLASS=FunctionalTestCase", '    \
          'with sauce "export TEST_CASE_CLASS=Selenium2OnSauce".'
    sys.exit()
except ImportError:
    print "Can't import '%s'" % os.environ['TEST_CASE_CLASS']
    sys.exit()



class LoginTests(TEST_CASE_CLASS):
    def test_1_existing_users_login(self):
        driver = self.login()

        # verify organization listing scrumdo after login landing page
        self.assertTrue('Please pick your organization.' in driver.find_element(By.TAG_NAME,'body').text)

    def test_2_existing_users_login_openid(self):
        driver = self.driver
        driver.get(self.base_url + "/account/login")
        driver.find_element_by_id("openid_signin_button").click()
        driver.find_element_by_name("openid_url").clear()
        driver.find_element_by_name("openid_url").send_keys("https://openid.stackexchange.com/user/68f7142c-e45f-4204-8ab6-9100d500d1aa")
        driver.find_element_by_css_selector("input.button.orange").click()
        driver.find_element_by_id("email").clear()
        driver.find_element_by_id("email").send_keys("scrumdoselenium@gmail.com")
        driver.find_element_by_id("password").clear()
        driver.find_element_by_id("password").send_keys("cgcuUt87_scrumdoselenium")
        driver.find_element_by_css_selector("input.affiliate-button").click()

        # verify organization listing scrumdo after login landing page
        self.assertTrue('Please pick your organization.' in driver.find_element(By.TAG_NAME,'body').text)

    def test_3_existing_users_login_github(self):
        """
        This requires an environment based github app credentials configuration:
        Note that the following supposed to work only for http://localhost:9000!
        GITHUB_AUTH_URL = "https://github.com/login/oauth/authorize"
        GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
        GITHUB_CLIENT_ID = "431edb1c8a17af996a44"
        GITHUB_SECRET = "71d6da685e720e6de4adb82e3d12b280adb51fde"
        """
        driver = self.driver
        driver.get(self.base_url + "/account/login")
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "Sign in with GitHub"))).click()
        if WebDriverWait(driver, 10).until(EC.title_is(u'Sign in · GitHub')):
            driver.find_element_by_id("login_field").clear()
            driver.find_element_by_id("login_field").send_keys("scrumdoselenium")
            driver.find_element_by_id("password").clear()
            driver.find_element_by_id("password").send_keys("cgcuUt87_scrumdoselenium")
            driver.find_element_by_name("commit").click()
        if "Authorize access to your account" in driver.title:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "authorize"))).click()

        try: WebDriverWait(driver, 10).until(
            lambda x: 'Please pick your organization.' in
                      x.find_element(By.TAG_NAME,'body').text)
        except TimeoutException:
            self.assertTrue('Please pick your organization.' in
                            driver.find_element(By.TAG_NAME,'body').text)


    def test_4_existing_users_login_google(self):
        driver = self.driver
        driver.get(self.base_url + "/account/login")
        driver.find_element_by_css_selector("button.sign-in-buttin").click()
        driver.execute_script("document.getElementById('Email').value='scrumdoselenium@gmail.com';")
        driver.execute_script("document.getElementById('Passwd').value='scrumdotesting';")
        driver.find_element_by_id("signIn").click()
        for i in range(60):
            try:
                if self.is_element_present(By.XPATH, "//a[contains(@href, '/organization/create/')]"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")

        # verify organization listing scrumdo after login landing page
        self.assertTrue('Please pick your organization.' in driver.find_element(By.TAG_NAME,'body').text)

    def test_5_existing_users_login_stackexchange(self):
        self.logout(); driver = self.driver
        driver.get(self.base_url + "/account/login/")
        driver.find_element_by_xpath("(//button[@type='submit'])[2]").click()
        driver.find_element_by_id("email").clear()
        driver.find_element_by_id("email").send_keys("scrumdoselenium@gmail.com")
        driver.find_element_by_id("password").clear()
        driver.find_element_by_id("password").send_keys("cgcuUt87_scrumdoselenium")
        driver.find_element_by_css_selector("input.affiliate-button").click()

        # verify organization listing scrumdo after login landing page
        self.assertTrue('Please pick your organization.' in driver.find_element(By.TAG_NAME,'body').text)

if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(LoginTests("test_1_existing_users_login"))
    suite.addTest(LoginTests("test_2_existing_users_login_openid"))
    suite.addTest(LoginTests("test_3_existing_users_login_github"))
    suite.addTest(LoginTests("test_4_existing_users_login_google"))
    suite.addTest(LoginTests("test_5_existing_users_login_stackexchange"))
    result = unittest.TextTestRunner(buffer=True,verbosity=2,resultclass=TEST_RESULT_CLASS).run(suite)
