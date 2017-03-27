from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re

class ExistingUsersLoginGithub(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30)
        self.base_url = "http://localhost:9000"
        self.verificationErrors = []
    
    def test_3_existing_users_login_github(self):
        driver = self.driver
        driver.get(self.base_url + "/account/login")
        driver.find_element_by_link_text("Sign in with GitHub").click()
        driver.find_element_by_id("login_field").clear()
        driver.find_element_by_id("login_field").send_keys("scrumdoselenium")
        driver.find_element_by_id("password").clear()
        driver.find_element_by_id("password").send_keys("cgcuUt87_scrumdoselenium")
        driver.find_element_by_name("commit").click()
        driver.find_element_by_name("authorize").click()
        self.assertEquals('The easiest way to manage your Scrum projects.' in driver.find_element(By.TAG_NAME,'body').text, True)
    
    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException, e: return False
        return True
    
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
