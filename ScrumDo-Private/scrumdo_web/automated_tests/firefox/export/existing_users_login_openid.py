from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re

class ExistingUsersLoginOpenid(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30)
        self.base_url = "http://localhost:9000"
        self.verificationErrors = []
    
    def test_existing_users_login_openid(self):
        driver = self.driver
        driver.get(self.base_url + "/account/logout/")
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
        self.assertEquals('Please pick your organization.' in driver.find_element(By.TAG_NAME,'body').text, True)
    
    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException, e: return False
        return True
    
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
