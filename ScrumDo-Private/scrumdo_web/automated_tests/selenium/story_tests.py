# -*- coding: utf-8 -*-
import os, time
from django.conf import settings
from django.utils import unittest
from functional_test_case import  *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementNotVisibleException

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

class StoryTests(TEST_CASE_CLASS):
    def test_20_create_a_story(self):
        driver = self.login()
        driver = self.create_story("/projects/project/testproject/iteration/3", "test story")
        try: #check that the story has been successfully updated
            WebDriverWait(driver, 10).until(lambda x: "#1" in x.find_element(By.ID, "story_1").text)
        except TimeoutException as e: self.verificationErrors.append(str(e))

    def test_21_update_story(self):
        driver = self.login()
        driver.get(self.base_url + "/projects/project/testproject/iteration/3")
        driver.find_element_by_css_selector("a.edit-story-button").click()
        try: summary = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "(//textarea[@id='id_detail'])[2]")))
        except TimeoutException as e: self.verificationErrors.append(str(e))
        finally:
            summary.clear(); summary.send_keys("test edit story")
            driver.find_element_by_xpath("//input[@value='Update Story']").click()
        try: #check that the story has been successfully updated
            WebDriverWait(driver, 10).until(
                lambda x: "test edit story" in
                          x.find_element(By.TAG_NAME,'body').text)
        except TimeoutException as e: self.verificationErrors.append(str(e))

    def test_22_delete_story(self):
        driver = self.login()
        driver.get(self.base_url + "/projects/project/testproject/iteration/3")
        driver.find_element_by_css_selector("a.edit-story-button").click()
        try: delete_button = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//input[@value='Delete Story']")))
        except TimeoutException as e: self.verificationErrors.append(str(e))
        finally: delete_button.click(); alert = driver.switch_to_alert(); alert.accept()

        #check that the story has been successfully updated
        showing_story = lambda x: x.find_element_by_id("story_1").is_displayed()
        self.assertTrue(WebDriverWait(driver, 10, 1, (ElementNotVisibleException)).until_not(showing_story))

    def test_23_duplicate_story(self):
        driver = self.login()
        driver = self.create_story("/projects/project/testproject/iteration/3", "test story")
        try: WebDriverWait(driver, 10).until(lambda x: "#1" in x.find_element(By.ID, "story_list").text)
        except TimeoutException as e: self.verificationErrors.append(str(e))
        finally: driver.get(self.base_url + "/projects/project/testproject/iteration/3")
        driver.find_element_by_css_selector("a.edit-story-button").click()
        try: WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH, "//input[@value='Duplicate Story']"))).click()
        except TimeoutException: self.fail('EC.element_to_be_clickable((By.XPATH, "Duplicate Story"))')
        try: #check that the story has been successfully updated
            WebDriverWait(driver, 10).until(lambda x: "#2" in x.find_element(By.ID, "story_list").text)
        except TimeoutException as e: self.verificationErrors.append(str(e))

    def test_24_add_attachment_to_a_story(self):
        iteration_url = self.base_url+"/projects/project/testproject/iteration/3"
        driver = self.login(); driver.get(iteration_url)
        driver.find_element_by_css_selector("a[title=\"Attach a file\"]").click()
        fpath = driver.find_element_by_id("id_attachment_file-2")
        fpath.send_keys("%s/automated_tests/story_attachment.txt" % settings.PROJECT_ROOT)
        driver.find_element_by_id("upload_button-2").click(); driver.get(iteration_url)
        WebDriverWait(driver, 60).until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR,"div.story_footer i.icon-paper-clip")), "story attachment file upload timeout")

    def test_26_update_story_status(self):
        iteration_url = self.base_url+"/projects/project/testproject/iteration/3"
        driver = self.login(); driver.get(iteration_url)

        driver.find_element_by_css_selector("a.edit-story-button").click()
        try: WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "id_status_1"))).click()
        except TimeoutException: self.fail("can't locate (By.ID, \"id_status_1\")")
        driver.find_element_by_xpath("//input[@value='Update Story']").click()
        try: driver.get(iteration_url); WebDriverWait(driver, 10).until(
            lambda x: 'Doing' in x.find_element_by_id('story_1').text)
        except TimeoutException: self.fail("'Doing' in x.find_element_by_id('story_1').text")

        driver.find_element_by_css_selector("a.edit-story-button").click()
        try: WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "id_status_2"))).click()
        except TimeoutException: self.fail("can't locate (By.ID, \"id_status_2\")")
        driver.find_element_by_xpath("//input[@value='Update Story']").click()
        try: driver.get(iteration_url); WebDriverWait(driver, 10).until(
            lambda x: 'Reviewing' in x.find_element_by_id('story_1').text)
        except TimeoutException: self.fail("'Reviewing' in x.find_element_by_id('story_1').text")

        driver.find_element_by_css_selector("a.edit-story-button").click()
        try: WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "id_status_3"))).click()
        except TimeoutException: self.fail("can't locate (By.ID, \"id_status_3\")")
        driver.find_element_by_xpath("//input[@value='Update Story']").click()
        try: driver.get(iteration_url); WebDriverWait(driver, 10).until(
            lambda x: 'Done' in x.find_element_by_id('story_1').text)
        except TimeoutException: self.fail("'Done' in x.find_element_by_id('story_1').text")

    def test_27_add_comments_to_story(self):
        driver = self.login()
        driver.get(self.base_url + "/projects/project/testproject/iteration/3")
        driver.find_element_by_partial_link_text("Comments").click()
        try: comment_box = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//*[@id=\"id_comment\"]")))
        except TimeoutException: self.fail('(By.XPATH, "//*[@id=\"id_comment\"]")')
        finally: comment_box.clear(); comment_box.send_keys("test comment")
        driver.find_element_by_xpath("//input[@value='Post Comment']").click()
        try: WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT,"1 Comment")))
        except TimeoutException: self.fail('EC.element_to_be_clickable((By.LINK_TEXT,"1 Comment"))')

    def test_28_add_tasks_to_story(self):
        iteration_url = self.base_url+"/projects/project/testproject/iteration/3"
        driver = self.login(); driver.get(iteration_url)
        driver.find_element_by_partial_link_text("Tasks:").click()
        summary = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "txtSummary")),
                                                  "task summary field 10 seconds wait timeout had arized")
        summary.clear(); summary.send_keys("test task")
        driver.find_element_by_id("newTaskButton").click()
        driver.find_element_by_link_text("Close").click(); driver.get(iteration_url)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT,"Tasks: 1")),
                                        "10s wait timeout: can't locate link text 'Tasks: 1'")

    def test_29_update_tasks_of_story(self):
        iteration_url = self.base_url+"/projects/project/testproject/iteration/3"
        driver = self.login(); driver.get(iteration_url)
        driver.find_element_by_partial_link_text("Tasks: 1").click()
        summary = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "txtSummary")),
                                                  "task summary field 10 seconds wait timeout had arized")
        driver.find_element_by_class_name("edit-link").click()
        summary.clear(); summary.send_keys("test task updated")
        driver.find_element_by_id("newTaskButton").click()
        WebDriverWait(driver, 10).until(
            lambda x: 'test task updated' in x.find_element(By.CLASS_NAME,'task-view').text,
            "10 seconds wait timeout: 'test task updated' text not found within 'task-view'")

    @unittest.skipIf(TEST_CASE_CLASS is Selenium2OnSauce, "sauce web sockets pusher limitation")
    def test_31_add_points_to_story_using_planing_poker(self):
        driver = self.login()
        driver.get(self.base_url + "/poker/play/testproject")
        driver.find_element_by_link_text("Become Scrum Master").click()
        time.sleep(1)
        alert = driver.switch_to_alert(); alert.accept()
        driver.execute_script("window.scrollTo(0,300);")
        driver.find_element_by_xpath("//a[contains(@href, '/projects/story/1')]").click()
        try: WebDriverWait(driver, 10).until(EC.visibility_of_element_located(
            (By.XPATH, "//a[contains(text(),'5')][2]"))).click()
        except TimeoutException: self.fail('(By.XPATH, "//a[contains(text(),\'5\')][2]")')
        finally: driver.find_element_by_link_text("Save").click()
        driver.get(self.base_url + "/projects/project/testproject/iteration/3")
        try: WebDriverWait(driver, 10).until(EC.text_to_be_present_in_element(
            (By.CSS_SELECTOR, 'li#story_1.story_block div.pointsBox'), "5"))
        except TimeoutException: self.fail("(By.CSS_SELECTOR,'li#story_1 div.pointsBox')")

    def test_32_update_story_points(self):
        driver = self.login()
        driver.get(self.base_url + "/projects/project/testproject/iteration/3")
        try: WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "#story_2 a.edit-story-button"))).click()
        except TimeoutException: self.fail('(By.CSS_SELECTOR, "#story_2 a.edit-story-button")')
        finally: driver.find_element_by_xpath("(//input[@id='id_points_6'])[2]").click()
        driver.find_element_by_xpath("//input[@value='Update Story']").click()
        try: WebDriverWait(driver, 10).until(
            lambda x: "5" in x.find_element(By.CSS_SELECTOR, 'li#story_2 div.pointsBox').text)
        except TimeoutException: self.fail("(By.CSS_SELECTOR, 'li#story_2 div.pointsBox')")


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(StoryTests("test_20_create_a_story"))
    suite.addTest(StoryTests("test_21_update_story"))
    suite.addTest(StoryTests("test_22_delete_story"))
    suite.addTest(StoryTests("test_23_duplicate_story"))
    suite.addTest(StoryTests("test_24_add_attachment_to_a_story"))
    suite.addTest(StoryTests("test_26_update_story_status"))
    suite.addTest(StoryTests("test_27_add_comments_to_story"))
    suite.addTest(StoryTests("test_28_add_tasks_to_story"))
    suite.addTest(StoryTests("test_29_update_tasks_of_story"))
    suite.addTest(StoryTests("test_31_add_points_to_story_using_planing_poker"))
    suite.addTest(StoryTests("test_32_update_story_points"))
    result = unittest.TextTestRunner(buffer=True,verbosity=2,resultclass=ScrumDoTestResult).run(suite)
