from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re

class ExistingUsersLoginGoogle(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30)
        self.base_url = "http://localhost:9000"
        self.verificationErrors = []
    
    def test_existing_users_login_google(self):
        driver = self.driver
        driver.get(self.base_url + "/account/logout")
        driver.get(self.base_url + "/account/login")
        driver.find_element_by_css_selector("button.sign-in-buttin").click()
        driver.find_element_by_id("Email").clear()
        driver.find_element_by_id("Email").send_keys("scrumdoselenium@gmail.com")
        driver.find_element_by_id("Passwd").clear()
        driver.find_element_by_id("Passwd").send_keys("scrumdotesting")
        driver.find_element_by_id("signIn").click()
        for i in range(60):
            try:
                if self.is_element_present(By.XPATH, "//*[@id=\"body\"]"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
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
