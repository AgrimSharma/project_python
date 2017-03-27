from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re

class SearchStoriesUsingSearchbox(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30)
        self.base_url = "http://localhost:9000/"
        self.verificationErrors = []
    
    def test_36_search_stories_using_searchbox(self):
        driver = self.driver
        driver.get(self.base_url + "/account/logout/")
        driver.get(self.base_url + "/account/login")
        driver.find_element_by_id("id_username").clear()
        driver.find_element_by_id("id_username").send_keys("scrumdoselenium")
        driver.find_element_by_id("id_password").clear()
        driver.find_element_by_id("id_password").send_keys("scrumdotesting")
        driver.find_element_by_xpath("//input[@value='Log In »']").click()
        driver.get(self.base_url + "/organization/testorg/dashboard")
        driver.find_element_by_id("searchProjectField").click()
        driver.find_element_by_id("searchProjectField").clear()
        driver.find_element_by_id("searchProjectField").send_keys("Last imported story")
        driver.find_element_by_xpath("//input[@value='Search']").click()
        try: self.assertTrue(self.is_element_present(By.XPATH, "//li[@id='story_7']/div/h1/span/a"))
        except AssertionError as e: self.verificationErrors.append(str(e))
    
    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException, e: return False
        return True
    
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
