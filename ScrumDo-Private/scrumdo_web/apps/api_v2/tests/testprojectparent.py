from django.test import TestCase
from django.conf import settings

import json

# sample_organization provides the following:
#
# organization: test-organization
# projects: test-project training29957
# users: staff read write
#
# org/projects are set up as in their intitial states except for the creation of some additional teams.


class ProjectParentTest(TestCase):
    fixtures = ["sample_organization.json"]

    def setUp(self):
        settings.ROLLBAR['access_token'] = ''
        settings.ROLLBAR['environment'] = ''
        logged_in = self.client.login(username="staff", password="staff")
        self.assertTrue(logged_in)

    def test_project_parent(self):
        content = self.client.get("/api/v3/organizations/test-organization/projects").content
        projects = json.loads(content)
        parent = projects[0]
        child = projects[1]

        # Can't set self parent
        child['parents'] = [{'id': child['id']}]
        response = self.client.put("/api/v3/organizations/test-organization/projects/%s" % child['slug'],
                                  content_type='application/json',
                                  data=json.dumps(child))
        self.assertEqual(response.status_code, 400)

        # Set a parent
        child['parents'] = [parent]
        content = self.client.put("/api/v3/organizations/test-organization/projects/%s" % child['slug'],
                                  content_type='application/json',
                                  data=json.dumps(child)).content
        response = json.loads(content)
        self.assertEqual(response['parents'][0]['id'], parent['id'])

        # Set it again, shouldn't change it.
        content = self.client.put("/api/v3/organizations/test-organization/projects/%s" % child['slug'],
                                  content_type='application/json',
                                  data=json.dumps(child)).content
        response = json.loads(content)
        self.assertEqual(response['parents'][0]['id'], parent['id'])


        # Can't create circular dependency
        parent['parents'] = [{'id': child['id']}]
        response = self.client.put("/api/v3/organizations/test-organization/projects/%s" % parent['slug'],
                                  content_type='application/json',
                                  data=json.dumps(parent))
        self.assertEqual(response.status_code, 400)





