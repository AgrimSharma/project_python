# -*- coding: utf-8 -*-
import os, time, datetime
from django.conf import settings
from django.utils import unittest
from functional_test_case import  *
from selenium.webdriver.common.by import By
from fabfile import update_search as solr_update
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

class IterationTests(TEST_CASE_CLASS):
    def test_42_create_new_iteration(self):
        driver = self.login()
        start_date = datetime.datetime.today()
        iteration_size = datetime.timedelta(days=30)
        deadline_date = start_date + iteration_size
        driver.get(self.base_url + "/projects/project/testproject/iteration_create")
        driver.find_element_by_id("id_name").clear()
        driver.find_element_by_id("id_name").send_keys("TestIteration")
        driver.find_element_by_id("id_start_date").clear()
        driver.find_element_by_id("id_start_date").send_keys(start_date.strftime("%Y-%m-%d"))
        driver.find_element_by_id("id_end_date").clear()
        driver.find_element_by_id("id_end_date").send_keys(deadline_date.strftime("%Y-%m-%d"))
        driver.find_element_by_css_selector("button.primaryAction").click()
        try: WebDriverWait(driver, 10).until(
            lambda x: "TestIteration" in x.find_element(By.TAG_NAME,"body").text)
        except TimeoutException: self.fail('"TestIteration" in x.find_element(By.TAG_NAME,"body").text')

    def test_43_add_stories_to_iteration(self):
        driver = self.login()
        driver.get(self.base_url + "/projects/project/testproject/stories/")
        Select(driver.find_element_by_id("iterationChooser")).select_by_visible_text("TestIteration")
        self.mouse.drag_and_drop(
            driver.find_element_by_css_selector("#backlog_div li#story_2"),
            driver.find_element_by_css_selector("#story_div ul#iteration_column")
        ).perform()
        driver.get(self.base_url + "/projects/project/testproject/iteration/5")
        try: WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "#2")))
        except TimeoutException: self.fail('EC.element_to_be_clickable((By.LINK_TEXT, "#2"))')

    def test_38_move_story_from_one_iteration_to_other(self):
        driver = self.login()
        driver.get(self.base_url + "/projects/project/testproject/stories/")
        Select(driver.find_element_by_xpath("//select[@id='iterationChooser']")).select_by_visible_text("TestIteration")
        time.sleep(2)
        self.mouse.drag_and_drop(
            driver.find_element_by_css_selector("#backlog_div li#story_1"),
            driver.find_element_by_css_selector("#story_div ul#iteration_column")
        ).perform()
        driver.get(self.base_url + "/projects/project/testproject/iteration/5")
        try: WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "#1")))
        except TimeoutException: self.fail('EC.element_to_be_clickable((By.LINK_TEXT, "#1"))')

    def test_37_filter_stories_order_various_criteria(self):
        solr_update(); driver = self.login()
        driver.get(self.base_url + "/projects/project/testproject/iteration/5")
        driver.execute_script("window.scrollTo(0,350);")
        driver.find_element_by_xpath("//a[contains(@href, '#filterDialog')]").click()
        driver.find_element_by_xpath("//a[contains(@href, '/projects/project/testproject/search_builder')]").click()
        driver.find_element_by_xpath("//input[@class='search-criteria']").clear()
        driver.find_element_by_xpath("//input[@class='search-criteria']").send_keys("test")
        Select(driver.find_element_by_xpath("//select[@name='order']")).select_by_visible_text("Number")
        driver.execute_script("window.scrollTo(0,350);")
        driver.find_element_by_xpath("(//button[@type='submit'])[3]").click()
        try: WebDriverWait(driver, 30).until(
            lambda x: "#1" in x.find_elements_by_css_selector(
                "ul#story_list.iteration_story_list li")[0].text)
        except TimeoutException: self.fail("can't find story #1")



if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(IterationTests("test_42_create_new_iteration"))
    suite.addTest(IterationTests("test_43_add_stories_to_iteration"))
    suite.addTest(IterationTests("test_38_move_story_from_one_iteration_to_other"))
    suite.addTest(IterationTests("test_37_filter_stories_order_various_criteria"))
    result = unittest.TextTestRunner(buffer=True,verbosity=2,resultclass=ScrumDoTestResult).run(suite)

