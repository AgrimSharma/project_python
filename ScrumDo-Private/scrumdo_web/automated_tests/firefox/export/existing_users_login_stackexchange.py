from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re

class ExistingUsersLoginStackexchange(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30)
        self.base_url = "http://localhost:9000"
        self.verificationErrors = []
    
    def test_existing_users_login_stackexchange(self):
        driver = self.driver
        driver.get(self.base_url + "/account/login/")
        driver.find_element_by_xpath("(//button[@type='submit'])[2]").click()
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
