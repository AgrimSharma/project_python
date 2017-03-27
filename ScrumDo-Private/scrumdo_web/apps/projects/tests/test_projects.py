# sample_organization provides the following:
#
# organization: test-organization
# projects: test-project training29957
# users: staff read write
#
# org/projects are set up as in their intitial states except for the creation of some additional teams.

from django.test import TestCase
from django.conf import settings

# Basic set of tests that just hits all the configured urls and checks status code

import logging

logger = logging.getLogger(__name__)
settings.ROLLBAR['access_token'] = ''
settings.ROLLBAR['environment'] = ''


class ProjectsTest(TestCase):
    fixtures = ["sample_organization.json"]

    def setUp(self):
        settings.ROLLBAR['access_token'] = ''
        settings.ROLLBAR['environment'] = ''

    def _test_page(self, url, requires_write, requires_staff, expected_template_name, code=200):
        logged_in = self.client.login(username="staff", password="staff")
        self.assertTrue(logged_in)
        response = self.client.get(url)
        self.assertEqual(response.status_code, code)
        if expected_template_name != False:
            self.assertTemplateUsed(response, expected_template_name)

        logged_in = self.client.login(username="read", password="read")
        self.assertTrue(logged_in)
        response = self.client.get(url)
        if requires_write:
            self.assertNotEqual(response.status_code, code)
        else:
            self.assertEqual(response.status_code, code)
            if expected_template_name != False:
                self.assertTemplateUsed(response, expected_template_name)

        logged_in = self.client.login(username="write", password="write")
        self.assertTrue(logged_in)
        response = self.client.get(url)
        if requires_staff:
            self.assertNotEqual(response.status_code, code)
        else:
            self.assertEqual(response.status_code, code)
            if expected_template_name != False:
                self.assertTemplateUsed(response, expected_template_name)

    def test_dashboard(self):
        """Test the dashboard page."""

        # not logged in
        response = self.client.get("/organization/test-organization/dashboard")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["location"], "/account/login/?next=/organization/test-organization/dashboard")

        logged_in = self.client.login(username="staff", password="XXX")
        self.assertFalse(logged_in)

        self._test_page("/organization/test-organization/dashboard", False, False, 'organizations/organization_dashboard.html')



    def test_board(self):
        self._test_page("/projects/test-project/board", False, False, False, 302)

    def test_predictions(self):
        self._test_page("/projects/project/test-project/project_prediction", False, False, 'projects/project_prediction.html')

    def test_project_search(self):
        self._test_page("/projects/project/test-project/search", False, False, False, 302)

    def test_project_create(self):
        self._test_page("/projects/project/test-organization/create", True, True, 'projects/create.html')

    def test_milestones(self):
        self._test_page("/projects/test-project/milestones", False, False, 'projects/milestones.html')

    def test_storyqueue(self):
        self._test_page("/projects/test-project/storyqueue", True, False, 'projects/story_queue.html')

    def test_tips(self):
        self._test_page("/projects/test-organization/test-project/tips", False, False, 'projects/tips.html')