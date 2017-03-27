from django.test.utils import setup_test_environment, teardown_test_environment
from django.core.management import call_command
from functional_test_case import *
from django.utils import unittest
from django.conf import settings
import login_tests
import account_tests
import project_tests
import team_tests
import excel_tests
import epic_tests
import story_tests
import iteration_tests
import shutil
import os,sys

try:
    # defines which resultclass to use
    if os.environ['TEST_CASE_CLASS'] == 'FunctionalTestCase':
        TEST_RESULT_CLASS = ScrumDoTestResult
    else: TEST_RESULT_CLASS = SauceTestResult
except KeyError:
    print '"TEST_CASE_CLASS" environment variable not found, to '\
          'locally "export TEST_CASE_CLASS=FunctionalTestCase", '\
          'with sauce "export TEST_CASE_CLASS=Selenium2OnSauce".'
    sys.exit()

def run_tests(test_environment = True):
    suite = unittest.TestSuite()

    suite.addTest(login_tests.LoginTests("test_1_existing_users_login"))
    suite.addTest(login_tests.LoginTests("test_2_existing_users_login_openid"))
    suite.addTest(login_tests.LoginTests("test_3_existing_users_login_github"))
    suite.addTest(login_tests.LoginTests("test_4_existing_users_login_google"))
    suite.addTest(login_tests.LoginTests("test_5_existing_users_login_stackexchange"))

    suite.addTest(account_tests.AccountTests("test_6_create_account_for_new_users"))
    suite.addTest(account_tests.AccountTests("test_7_create_a_new_organization_subscription"))
    suite.addTest(account_tests.AccountTests("test_8_update_organization"))
    suite.addTest(account_tests.AccountTests("test_40_add_message_to_scrumlog"))
    suite.addTest(account_tests.AccountTests("test_41_switch_organization"))

    suite.addTest(excel_tests.ExcelTests("test_35_import_iteration_from_spreadsheet"))
    suite.addTest(excel_tests.ExcelTests("test_34_export_iteration_to_spreadsheet"))
    suite.addTest(excel_tests.ExcelTests("test_33_export_project_to_spreadsheet"))
    suite.addTest(excel_tests.ExcelTests("test_16_organization_data_export_to_excel"))

    suite.addTest(project_tests.ProjectTests("test_9_create_a_project"))
    suite.addTest(project_tests.ProjectTests("test_10_update_project_settings"))
    suite.addTest(project_tests.ProjectTests("test_11_delete_project"))
    suite.addTest(project_tests.ProjectTests("test_12_archive_project"))

    suite.addTest(team_tests.TeamTests("test_13_create_a_team"))
    suite.addTest(team_tests.TeamTests("test_14_delete_team"))
    suite.addTest(team_tests.TeamTests("test_15_add_users_to_team"))

    suite.addTest(epic_tests.EpicTests("test_17_create_epic"))
    suite.addTest(epic_tests.EpicTests("test_18_update_epic"))
    suite.addTest(epic_tests.EpicTests("test_19_delete_epic"))

    suite.addTest(story_tests.StoryTests("test_20_create_a_story"))
    suite.addTest(story_tests.StoryTests("test_21_update_story"))
    suite.addTest(story_tests.StoryTests("test_22_delete_story"))
    suite.addTest(story_tests.StoryTests("test_23_duplicate_story"))
    suite.addTest(story_tests.StoryTests("test_24_add_attachment_to_a_story"))
    suite.addTest(story_tests.StoryTests("test_26_update_story_status"))
    suite.addTest(story_tests.StoryTests("test_27_add_comments_to_story"))
    suite.addTest(story_tests.StoryTests("test_28_add_tasks_to_story"))
    suite.addTest(story_tests.StoryTests("test_29_update_tasks_of_story"))
    suite.addTest(story_tests.StoryTests("test_31_add_points_to_story_using_planing_poker"))
    suite.addTest(story_tests.StoryTests("test_32_update_story_points"))

    suite.addTest(iteration_tests.IterationTests("test_42_create_new_iteration"))
    suite.addTest(iteration_tests.IterationTests("test_43_add_stories_to_iteration"))
    suite.addTest(iteration_tests.IterationTests("test_38_move_story_from_one_iteration_to_other"))
    suite.addTest(iteration_tests.IterationTests("test_37_filter_stories_order_various_criteria"))


    if test_environment:
        setup_test_environment()
        call_command('flush', verbosity=1, interactive=False)
    result = unittest.TextTestRunner(buffer=True,verbosity=2,resultclass=TEST_RESULT_CLASS).run(suite)
    result.dump_xml("%s/automated_tests/results" % settings.PROJECT_ROOT)
    if test_environment: teardown_test_environment()

if __name__ == "__main__":
    if os.path.exists(settings.TEST_DB): os.unlink(settings.TEST_DB)
    if os.path.exists("%s.backup" % settings.TEST_DB):
        print "Restoring 'database.db.backup' testing db build!"
        shutil.copy2("%s.backup" % settings.TEST_DB, settings.TEST_DB)
        run_tests(test_environment=False)
    else: run_tests()