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


class OrganizationAPITest(TestCase):
    fixtures = ["sample_organization.json"]

    def setUp(self):
        settings.ROLLBAR['access_token'] = ''
        settings.ROLLBAR['environment'] = ''

    def test_organization_api(self):
        logged_in = self.client.login(username="test", password="test")
        self.assertTrue(logged_in)
        response = self.client.get("/api/v3/organizations/test-organization")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(content, "You don't have access to that Organization")

        logged_in = self.client.login(username="read", password="read")
        self.assertTrue(logged_in)
        response = self.client.get("/api/v3/organizations/")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content[0]['slug'], 'test-organization')
        self.assertEqual(content[0]['name'], 'Test Organization')
        self.assertEqual(len(content), 1)

        response = self.client.post("/api/v3/organizations/test-organization",
                                    content_type='application/json',
                                    data=json.dumps({'name':'xxx'}))
        self.assertEqual(response.status_code, 405)

        response = self.client.put("/api/v3/organizations/test-organization",
                                   content_type='application/json',
                                   data=json.dumps({'planning_mode': "portfolio"}))
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(content, "You can not update this organization.")

        logged_in = self.client.login(username="write", password="write")
        self.assertTrue(logged_in)

        response = self.client.put("/api/v3/organizations/test-organization",
                                   content_type='application/json',
                                   data=json.dumps({'planning_mode': "portfolio"}))
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(content, "You can not update this organization.")

        logged_in = self.client.login(username="staff", password="staff")
        self.assertTrue(logged_in)

        response = self.client.put("/api/v3/organizations/test-organization",
                                   content_type='application/json',
                                   data=json.dumps({'name':'xxx'}))
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/api/v3/organizations/")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content[0]['slug'], 'test-organization')
        self.assertEqual(content[0]['name'], 'xxx')
        self.assertEqual(len(content), 1)

        response = self.client.get("/api/v3/organizations/test-organization")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['slug'], 'test-organization')
        self.assertEqual(content['name'], 'xxx')

    def test_organization_user(self):
        logged_in = self.client.login(username="test", password="test")
        self.assertTrue(logged_in)
        response = self.client.post("/api/v3/organizations/test-organization/me",
                                    content_type='application/json',
                                    data=json.dumps({'name':'xxx'}))
        self.assertEqual(response.status_code, 405)

        response = self.client.put("/api/v3/organizations/test-organization/me",
                                   content_type='application/json',
                                   data=json.dumps({'name':'xxx'}))
        self.assertEqual(response.status_code, 405)

        response = self.client.get("/api/v3/organizations/test-organization/me")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(content, "You don't have access to that Organization")

        logged_in = self.client.login(username="read", password="read")
        self.assertTrue(logged_in)
        response = self.client.get("/api/v3/organizations/test-organization/me")
        self.assertEqual(response.status_code, 200)

        logged_in = self.client.login(username="staff", password="staff")
        self.assertTrue(logged_in)
        response = self.client.get("/api/v3/organizations/test-organization/me")
        self.assertEqual(response.status_code, 200)

    def test_organization_users(self):
        logged_in = self.client.login(username="read", password="read")
        self.assertTrue(logged_in)

        response = self.client.post("/api/v3/organizations/test-organization/users",
                                    content_type='application/json',
                                    data=json.dumps({'name':'xxx'}))
        self.assertEqual(response.status_code, 405)

        response = self.client.put("/api/v3/organizations/test-organization/users",
                                   content_type='application/json',
                                   data=json.dumps({'name':'xxx'}))
        self.assertEqual(response.status_code, 405)

        response = self.client.get("/api/v3/organizations/test-organization/users")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        #next: after rework of org.members the content has to be verified

        logged_in = self.client.login(username="staff", password="staff")
        self.assertTrue(logged_in)
        response = self.client.get("/api/v3/organizations/test-organization/users")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        #next: after rework of org.members the content has to be verified

    def test_organization_teams(self):
        logged_in = self.client.login(username="test", password="test")
        self.assertTrue(logged_in)
        response = self.client.get("/api/v3/organizations/test-organization/teams")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(content, "You do not have access to view this")

        response = self.client.put("/api/v3/organizations/test-organization/teams",
                                   content_type='application/json',
                                   data=json.dumps({'name':'xxx'}))
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(content, "You do not have access to do this")

        response = self.client.post("/api/v3/organizations/test-organization/teams",
                                    content_type='application/json',
                                    data=json.dumps({'name':'xxx'}))
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(content, "You do not have access to do this")

        response = self.client.delete("/api/v3/organizations/test-organization/teams/3")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(content, "You do not have access to do this")

        logged_in = self.client.login(username="read", password="read")
        self.assertTrue(logged_in)
        response = self.client.get("/api/v3/organizations/test-organization/teams")
        self.assertEqual(response.status_code, 200)

        response = self.client.put("/api/v3/organizations/test-organization/teams",
                                   content_type='application/json',
                                   data=json.dumps({'name':'xxx'}))
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(content, "You do not have access to do this")

        response = self.client.post("/api/v3/organizations/test-organization/teams",
                                    content_type='application/json',
                                    data=json.dumps({'name':'xxx'}))
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(content, "You do not have access to do this")

        response = self.client.delete("/api/v3/organizations/test-organization/teams/3")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(content, "You do not have access to do this")

        logged_in = self.client.login(username="staff", password="staff")
        self.assertTrue(logged_in)
        response = self.client.post("/api/v3/organizations/test-organization/teams",
                                    content_type='application/json',
                                    data=json.dumps({'name':'xxx'}))
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content["access_type"], "write")

        response = self.client.get("/api/v3/organizations/test-organization/teams")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content[4]['name'], 'xxx')

        response = self.client.put("/api/v3/organizations/test-organization/teams/5",
                                   content_type='application/json',
                                   data=json.dumps({'name':'new'}))
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['name'], 'new')

        response = self.client.delete("/api/v3/organizations/test-organization/teams/5")
        self.assertEqual(response.status_code, 200)

    def test_active_stories(self):
        logged_in = self.client.login(username="test", password = "test")
        self.assertTrue(logged_in)
        response = self.client.get("/api/v3/organizations/test-organization/active_stories")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(content, "You don't have access to that organization")

        logged_in = self.client.login(username="read", password = "read")
        self.assertTrue(logged_in)
        response = self.client.put("/api/v3/organizations/test-organization/active_stories",
                                   content_type='application/json',
                                   data=json.dumps({}))
        self.assertEqual(response.status_code, 405)

        response = self.client.post("/api/v3/organizations/test-organization/active_stories",
                                   content_type='application/json',
                                   data=json.dumps({}))
        self.assertEqual(response.status_code, 405)

        response = self.client.get("/api/v3/organizations/test-organization/active_stories")
        self.assertEqual(response.status_code, 200)

        logged_in = self.client.login(username="staff", password = "staff")
        self.assertTrue(logged_in)
        response = self.client.put("/api/v3/organizations/test-organization/active_stories",
                                   content_type='application/json',
                                   data=json.dumps({}))
        self.assertEqual(response.status_code, 405)

        response = self.client.post("/api/v3/organizations/test-organization/active_stories",
                                   content_type='application/json',
                                   data=json.dumps({}))
        self.assertEqual(response.status_code, 405)

        response = self.client.get("/api/v3/organizations/test-organization/active_stories")
        self.assertEqual(response.status_code, 200)

    def test_subsciption_plan(self):
        loggen_in = self.client.login(username="test", password="test")
        self.assertTrue(loggen_in)
        response = self.client.post("/api/v3/organizations/subscription/",
                                    content_type='application/json',
                                    data=json.dumps({}))
        self.assertEqual(response.status_code, 405)

        response = self.client.put("/api/v3/organizations/subscription/",
                                    content_type='application/json',
                                    data=json.dumps({}))
        self.assertEqual(response.status_code, 405)

        response = self.client.get("/api/v3/organizations/subscription/")
        self.assertEqual(response.status_code, 200)

        loggen_in = self.client.login(username="staff", password="staff")
        self.assertTrue(loggen_in)
        response = self.client.get("/api/v3/organizations/subscription/")
        self.assertEqual(response.status_code, 200)

    def test_subscription(self):
        loggen_in = self.client.login(username="test", password="test")
        self.assertTrue(loggen_in)
        response = self.client.get("/api/v3/organizations/test-organization/subscription/")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(content, "You don't have access to that Organization")

        loggen_in = self.client.login(username="read", password="read")
        self.assertTrue(loggen_in)
        response = self.client.get("/api/v3/organizations/test-organization/subscription/")
        self.assertEqual(response.status_code, 200)

    def test_subscription_code(self):
        logged_in = self.client.login(username="read", password = "read")
        self.assertTrue(logged_in)
        response = self.client.post("/api/v3/organizations/test-organization/subscription/code/",
                                    content_type='application/json',
                                    data=json.dumps({'code':'33'}))
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(content, "Only staff members can do this")

        logged_in = self.client.login(username="staff", password = "staff")
        self.assertTrue(logged_in)
        response = self.client.post("/api/v3/organizations/test-organization/subscription/code/",
                                    content_type='application/json',
                                    data=json.dumps({'code':'3043'}))
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['status'], "Code Not Found")

        '''
        response = self.client.post("/api/v3/organizations/test-organization/subscription/code/",
                                    content_type='application/json',
                                    data=json.dumps({'code':'3043'}))
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['status'], "Subscription Code Applied")
        '''

    def test_project(self):
        logged_in = self.client.login(username="test", password = "test")
        self.assertTrue(logged_in)
        response = self.client.get("/api/v3/organizations/test-organization/projects")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(content, "You don't have access to that Organization")

        response = self.client.get("/api/v3/organizations/test-organization/projects/test-project")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(content, "You don't have access to that Organization")

        logged_in = self.client.login(username="read", password = "read")
        self.assertTrue(logged_in)
        response = self.client.get("/api/v3/organizations/test-organization/projects")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/api/v3/organizations/test-organization/projects/training29957")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(content, "You don't have access to that Project")

        response = self.client.get("/api/v3/organizations/test-organization/projects/test-project")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['name'], "Test Project")

        response = self.client.put("/api/v3/organizations/test-organization/projects/test-project",
                                   content_type='application/json',
                                   data=json.dumps({'name':'project', 'prefix': 'PP'}))
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(content, "You don't have access to that Project")

        logged_in = self.client.login(username="write", password = "write")
        self.assertTrue(logged_in)
        response = self.client.get("/api/v3/organizations/test-organization/projects")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/api/v3/organizations/test-organization/projects/training29957")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(content, "You don't have access to that Project")

        response = self.client.get("/api/v3/organizations/test-organization/projects/test-project")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['name'], "Test Project")

        response = self.client.put("/api/v3/organizations/test-organization/projects/test-project",
                                   content_type='application/json',
                                   data=json.dumps({'name':'project', 'prefix': 'PP'}))
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(content, "You don't have access to that Project")

        logged_in = self.client.login(username="staff", password = "staff")
        self.assertTrue(logged_in)
        response = self.client.get("/api/v3/organizations/test-organization/projects")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/api/v3/organizations/test-organization/projects/test-project")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['name'], "Test Project")

        response = self.client.get("/api/v3/organizations/test-organization/projects/training29957")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['name'], "Sample Project")

        response = self.client.put("/api/v3/organizations/test-organization/projects/test-project",
                                   content_type='application/json',
                                   data=json.dumps({'name':'project', 'prefix': 'PP'}))
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['name'], "project")
        self.assertEqual(content['prefix'], "PP")

    def test_search(self):
        logged_in = self.client.login(username="read", password = "read")
        self.assertTrue(logged_in)
        response = self.client.get("/api/v3/organizations/test-organization/search")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/api/v3/organizations/test-organization/projects/test-project/search")
        self.assertEqual(response.status_code, 200)
        '''
        response = self.client.get("/api/v3/organizations/test-organization/projects/test-project/iterations/(?P<iteration_id>[0-9,]+)/search")
        self.assertEqual(response.status_code, 200)
        '''
        logged_in = self.client.login(username="staff", password = "staff")
        self.assertTrue(logged_in)
        response = self.client.get("/api/v3/organizations/test-organization/search")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/api/v3/organizations/test-organization/projects/training29957/search")
        self.assertEqual(response.status_code, 200)
        '''
        response = self.client.get("/api/v3/organizations/test-organization/projects/training29957/iterations/(?P<iteration_id>[0-9,]+)/search")
        self.assertEqual(response.status_code, 200)
        '''

    def test_label(self):
        logged_in = self.client.login(username="write", password = "write")
        self.assertTrue(logged_in)
        response = self.client.get("/api/v3/organizations/test-organization/projects/test-project/labels")
        self.assertEqual(response.status_code, 200)

        response = self.client.post("/api/v3/organizations/test-organization/projects/test-project/labels",
                                    content_type='application/json',
                                    data=json.dumps({'id':'4','name':'testlabel','color':'16711680'}))
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['name'], "testlabel")

        response = self.client.put("/api/v3/organizations/test-organization/projects/test-project/labels/4",
                                    content_type='application/json',
                                    data=json.dumps({'name':'testrename'}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['name'], "testlabel") #its not updating!!!

        response = self.client.delete("/api/v3/organizations/test-organization/projects/test-project/labels/4")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content, "deleted")

    def test_project_access(self):
        logged_in = self.client.login(username="test", password = "test")
        self.assertTrue(logged_in)
        response = self.client.get("/api/v3/organizations/test-organization/projects/test-project/access/")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(content, "You don't have access to that Organization")

        logged_in = self.client.login(username="read", password = "read")
        self.assertTrue(logged_in)
        response = self.client.get("/api/v3/organizations/test-organization/projects/training29957/access/")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(content, "You don't have access to that Project")

        response = self.client.get("/api/v3/organizations/test-organization/projects/test-project/access/")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['access'], "read")

        logged_in = self.client.login(username="staff", password = "staff")
        self.assertTrue(logged_in)
        response = self.client.get("/api/v3/organizations/test-organization/projects/test-project/access/")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['access'], "admin")

    def test_project_stats(self):
        logged_in = self.client.login(username="test", password = "test")
        self.assertTrue(logged_in)
        response = self.client.get("/api/v3/organizations/test-organization/projects/test-project/stats")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(content, "You don't have access to that Organization")

        logged_in = self.client.login(username="read", password = "read")
        self.assertTrue(logged_in)
        response = self.client.get("/api/v3/organizations/test-organization/projects/training29957/stats")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(content, "You don't have access to that Project")

        response = self.client.get("/api/v3/organizations/test-organization/projects/test-project/stats")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)

    def test_burndown(self):
        logged_in = self.client.login(username="test", password = "test")
        self.assertTrue(logged_in)
        response = self.client.get("/api/v3/organizations/test-organization/projects/test-project/burndown")
        self.assertEqual(response.status_code, 403)

        logged_in = self.client.login(username="read", password = "read")
        self.assertTrue(logged_in)
        response = self.client.get("/api/v3/organizations/test-organization/projects/test-project/burndown")
        self.assertEqual(response.status_code, 200)

        #response = self.client.get("/api/v3/organization/test-organization/projects/test-project/iterations/2/burndown")
        #self.assertEqual(response.status_code, 200)

    def test_project_members(self):
        logged_in = self.client.login(username="test", password = "test")
        self.assertTrue(logged_in)
        response = self.client.get("/api/v3/organizations/test-organization/projects/test-project/members/")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(content, "You don't have access to that Organization")

        logged_in = self.client.login(username="read", password = "read")
        self.assertTrue(logged_in)
        response = self.client.get("/api/v3/organizations/test-organization/projects/training29957/members/")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(content, "You don't have access to that Project")

        response = self.client.get("/api/v3/organizations/test-organization/projects/test-project/members/")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 3)

    def test_iteration(self):
        logged_in = self.client.login(username="test", password = "test")
        self.assertTrue(logged_in)
        response = self.client.get("/api/v3/organizations/test-organization/projects/test-project/iterations")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(content, "You don't have access to that Organization")

        logged_in = self.client.login(username="read", password = "read")
        self.assertTrue(logged_in)
        response = self.client.get("/api/v3/organizations/test-organization/projects/test-project/iterations")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 3)

        logged_in = self.client.login(username="write", password = "write")
        self.assertTrue(logged_in)
        response = self.client.get("/api/v3/organizations/test-organization/projects/test-project/iterations")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 3)

        response = self.client.post("/api/v3/organizations/test-organization/projects/test-project/iterations",
                                    content_type='application/json',
                                    data=json.dumps({'name':'testiteration'}))
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/api/v3/organizations/test-organization/projects/test-project/iterations")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 4)

        response = self.client.put("/api/v3/organizations/test-organization/projects/test-project/iterations/7/",
                                    content_type='application/json',
                                    data=json.dumps({'name':'testiterationupdate'}))
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['name'], 'testiterationupdate')

        response = self.client.delete("/api/v3/organizations/test-organization/projects/test-project/iterations/7/")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content, 'deleted')

        response = self.client.get("/api/v3/organizations/test-organization/projects/test-project/iterations")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 3)

    def test_story(self):
        logged_in = self.client.login(username="test", password = "test")
        self.assertTrue(logged_in)
        response = self.client.get("/api/v3/organizations/test-organization/projects/test-project/stories")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(content, "You don't have access to that Organization")

        logged_in = self.client.login(username="write", password = "write")
        self.assertTrue(logged_in)
        response = self.client.get("/api/v3/organizations/test-organization/projects/test-project/stories")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['count'], 0)

        #iteration 1 -> 0 stories
        response = self.client.get("/api/v3/organizations/test-organization/projects/test-project/iterations/1/stories")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 0)

        response = self.client.post("/api/v3/organizations/test-organization/projects/test-project/iterations/1/stories",
                                    content_type='application/json',
                                    data=json.dumps({
                                                      "summary": "<p>add story</p>",
                                                      "relativeRank": 0,
                                                      "iteration_id": 1,
                                                      "detail": "<p>testvam</p>",
                                                      "tags": "t4",
                                                      "estimated_minutes": 0
                                                    }))
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['id'], 17)

        response = self.client.put("/api/v3/organizations/test-organization/projects/test-project/stories/17",
                                   content_type='application/json',
                                   data=json.dumps({"summary": "<p>updated story</p>"}))
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['summary'], '<p>updated story</p>')

        #iteration 1 -> 1 stories
        response = self.client.get("/api/v3/organizations/test-organization/projects/test-project/iterations/1/stories")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 1)

        response = self.client.delete("/api/v3/organizations/test-organization/projects/test-project/stories/17")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content, 'deleted')

        #iteration 1 -> 0 stories
        response = self.client.get("/api/v3/organizations/test-organization/projects/test-project/iterations/1/stories")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 0)

    def test_story_blockers(self):
        logged_in = self.client.login(username="staff", password = "staff")
        self.assertTrue(logged_in)

        response = self.client.post("/api/v3/organizations/test-organization/projects/test-project/iterations/1/stories",
                                    content_type='application/json',
                                    data=json.dumps({
                                                      "summary": "<p>add story for blockers</p>",
                                                      "relativeRank": 0,
                                                      "iteration_id": 1,
                                                      "detail": "<p>testvam</p>",
                                                      "tags": "t4",
                                                      "estimated_minutes": 0
                                                    }))
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        story_id = content['id']

        response = self.client.post("/api/v3/organizations/test-organization/projects/test-project/stories/%d/blockers/blocker" % story_id,
                                    content_type='application/json',
                                    data=json.dumps({
                                                      "reason": "this is a test blocker",
                                                      "external": True
                                                    }))
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["resolved"], False)
        self.assertEqual(content["external"], True)

        response = self.client.post("/api/v3/organizations/test-organization/projects/test-project/stories/%d/blockers/blocker" % story_id,
                                    content_type='application/json',
                                    data=json.dumps({
                                                      "reason": "this is a test internal blocker",
                                                      "external": False
                                                    }))
        content = json.loads(response.content)
        blocker_id = content["id"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["resolved"], False)
        self.assertEqual(content["external"], False)

        response = self.client.put("/api/v3/organizations/test-organization/projects/test-project/stories/%d/blockers/%d" % (story_id, blocker_id),
                                    content_type='application/json',
                                    data=json.dumps({
                                                      "resolution": "resolved a blocker"
                                                    }))
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["resolved"], True)

        response = self.client.get("/api/v3/organizations/test-organization/projects/test-project/stories/%d/blockers/blocker" % story_id)
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

        response = self.client.get("/api/v3/organizations/test-organization/projects/test-project/blockers/blocker")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content["blockers"]["common"]), 2)

        response = self.client.delete("/api/v3/organizations/test-organization/projects/test-project/stories/%d" % story_id)
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content, 'deleted')


    def test_story_move(self):
        logged_in = self.client.login(username="test", password = "test")
        self.assertTrue(logged_in)
        response = self.client.get("/api/v3/organizations/test-organization/projects/test-project/stories")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(content, "You don't have access to that Organization")

        logged_in = self.client.login(username="staff", password = "staff")
        self.assertTrue(logged_in)
        response = self.client.put("/api/v3/organizations/test-organization/projects/training29957/stories/16/movetoproject",
                                   content_type='application/json',
                                   data=json.dumps({'project_slug': 'test-project',
                                                    'iteration_id': '1'}))
        self.assertEqual(response.status_code, 200)

        #iteration 1 -> 0 stories
        response = self.client.get("/api/v3/organizations/test-organization/projects/test-project/iterations/1/stories")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 1)

        response = self.client.put("/api/v3/organizations/test-organization/projects/test-project/stories/16/movetoproject",
                                   content_type='application/json',
                                   data=json.dumps({'project_slug': 'training29957',
                                                    'iteration_id': '5'}))
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/api/v3/organizations/test-organization/projects/test-project/iterations/1/stories")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 0)

    def test_epic(self):
        logged_in = self.client.login(username="test", password = "test")
        self.assertTrue(logged_in)
        response = self.client.get("/api/v3/organizations/test-organization/projects/test-project/epics")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(content, "You don't have access to that Organization")

        logged_in = self.client.login(username="write", password = "write")
        self.assertTrue(logged_in)
        response = self.client.get("/api/v3/organizations/test-organization/projects/test-project/epics")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 0)

        response = self.client.post("/api/v3/organizations/test-organization/projects/test-project/epics",
                                    content_type='application/json',
                                    data=json.dumps({"detail": "testepic"}))
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['detail'], "testepic")

        response = self.client.get("/api/v3/organizations/test-organization/projects/test-project/epics/4")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['detail'], 'testepic')

        response = self.client.put("/api/v3/organizations/test-organization/projects/test-project/epics/4",
                                    content_type='application/json',
                                    data=json.dumps({"detail": "updatedepic"}))
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/api/v3/organizations/test-organization/projects/test-project/epics/4")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['detail'], 'updatedepic')

        response = self.client.delete("/api/v3/organizations/test-organization/projects/test-project/epics/4")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content, 'deleted')

        response = self.client.get("/api/v3/organizations/test-organization/projects/test-project/epics")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 0)

    def test_tasks(self):
        logged_in = self.client.login(username="test", password = "test")
        self.assertTrue(logged_in)
        response = self.client.get("/api/v3/organizations/test-organization/projects/test-project/iterations/5/stories/1/tasks")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(content, "You don't have access to that Organization")

        logged_in = self.client.login(username="staff", password = "staff")
        self.assertTrue(logged_in)
        response = self.client.get("/api/v3/organizations/test-organization/projects/training29957/iterations/5/stories/3/tasks")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 3)

        response = self.client.post("/api/v3/organizations/test-organization/projects/training29957/iterations/5/stories/3/tasks",
                                    content_type='application/json',
                                    data=json.dumps({"summary":"test_task",
                                                    "tags":"tag1, tag2",
                                                    "order":55,}))
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/api/v3/organizations/test-organization/projects/training29957/iterations/5/stories/3/tasks/4")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['summary'], 'test_task')
        '''
        response = self.client.put("/api/v3/organizations/test-organization/projects/training29957/iterations/5/stories/3/tasks/4",
                                    content_type='application/json',
                                    data=json.dumps({"summary":"updated_task"}))
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/api/v3/organizations/test-organization/projects/training29957/iterations/5/stories/3/tasks/4")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['summary'], 'updated_task')
        '''
        response = self.client.delete("/api/v3/organizations/test-organization/projects/training29957/iterations/5/stories/3/tasks/4")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/api/v3/organizations/test-organization/projects/training29957/iterations/5/stories/3/tasks")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 3)

        response = self.client.get("/api/v3/organizations/test-organization/projects/training29957/stories/3/tasks")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 3)

        response = self.client.post("/api/v3/organizations/test-organization/projects/training29957/stories/3/tasks",
                                    content_type='application/json',
                                    data=json.dumps({"summary":"test1_task",
                                                    "tags":"tag31",
                                                    "order":33,}))
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/api/v3/organizations/test-organization/projects/training29957/stories/3/tasks")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 4)

        response = self.client.get("/api/v3/organizations/test-organization/projects/training29957/stories/3/tasks/5")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['summary'], 'test1_task')
        '''
        response = self.client.put("/api/v3/organizations/test-organization/projects/training29957/stories/3/tasks/5",
                                    content_type='application/json',
                                    data=json.dumps({"summary":"updated1_task"}))
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/api/v3/organizations/test-organization/projects/training29957/stories/3/tasks/5")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['summary'], 'updated1_task')
        '''
        response = self.client.delete("/api/v3/organizations/test-organization/projects/training29957/stories/3/tasks/5")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/api/v3/organizations/test-organization/projects/training29957/stories/3/tasks")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 3)

    def test_time(self):
        #Uncomment when get is fixed
        logged_in = self.client.login(username="test", password = "test")
        self.assertTrue(logged_in)
        response = self.client.get("/api/v3/organizations/test-organization/projects/training29957/time_entries")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(content, "You don't have access to that Organization")

        logged_in = self.client.login(username="staff", password = "staff")
        self.assertTrue(logged_in)
        '''
        response = self.client.get("/api/v3/organizations/test-organization/projects/training29957/time_entries")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 0)
        '''
        response = self.client.post("/api/v3/organizations/test-organization/projects/training29957/stories/3/tasks",
                                    content_type='application/json',
                                    data=json.dumps({
                                                    "notes":"time entry test",
                                                    "date":2015-01-01
                                                    }))
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        '''
        response = self.client.get("/api/v3/organizations/test-organization/projects/training29957/time_entries")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['notes'], "time entry test")

        response = self.client.put("/api/v3/organizations/test-organization/projects/training29957/time_entries/1",
                                    content_type='application/json',
                                    data=json.dumps({
                                                    "notes":"time entry updated test"
                                                    }))
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/api/v3/organizations/test-organization/projects/training29957/time_entries")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['notes'], "time entry updated test")

        response = self.client.delete("/api/v3/organizations/test-organization/projects/training29957/time_entries/1")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/api/v3/organizations/test-organization/projects/training29957/time_entries")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 0)
        '''

    def test_comment(self):
        logged_in = self.client.login(username="test", password = "test")
        self.assertTrue(logged_in)
        response = self.client.get("/api/v3/comments/story/3")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 0)

        logged_in = self.client.login(username="staff", password = "staff")
        self.assertTrue(logged_in)
        response = self.client.get("/api/v3/comments/story/3")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 0)

        response = self.client.post("/api/v3/comments/story/3",
                                    content_type='application/json',
                                    data=json.dumps({"comment": "test comment"}))
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/api/v3/comments/story/3")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 1)

    def xtest_workflow(self):
        logged_in = self.client.login(username="test", password = "test")
        self.assertTrue(logged_in)
        response = self.client.get("/api/v3/organizations/test-organization/projects/training29957/workflows/1")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(content, "You don't have access to that Organization")

        logged_in = self.client.login(username="staff", password = "staff")
        self.assertTrue(logged_in)
        response = self.client.get("/api/v3/organizations/test-organization/projects/training29957/workflows/1")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['name'], 'Everything')

        response = self.client.put("/api/v3/organizations/test-organization/projects/training29957/workflows/1",
                                   content_type='application/json',
                                   data=json.dumps({'name':'updated workflow'}))
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/api/v3/organizations/test-organization/projects/training29957/workflows/1")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['name'], 'updated workflow')

        response = self.client.get("/api/v3/organizations/test-organization/projects/training29957/workflows")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 1)

        response = self.client.post("/api/v3/organizations/test-organization/projects/training29957/workflows",
                                   content_type='application/json',
                                   data=json.dumps({'name':'new workflow'}))
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/api/v3/organizations/test-organization/projects/training29957/workflows")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)
        '''
        response = self.client.get("/api/v3/organizations/test-organization/projects/training29957/workflows/1/steps")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200) #'QuerySet' object has no attribute 'orderBy'
        self.assertEqual(len(content), 4)
        '''
        response = self.client.post("/api/v3/organizations/test-organization/projects/training29957/workflows/1/steps",
                                   content_type='application/json',
                                   data=json.dumps(	{"name":"Workflow test",
                                                    "on_hold":'false',
                                                    "status_code":1,
                                                    "order":1 }))
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        '''
        response = self.client.get("/api/v3/organizations/test-organization/projects/training29957/workflows/1/steps/5")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200) #'WorkflowStep' object has no attribute 'orderBy'
        self.assertEqual(content['name'], 'Workflow test')

        response = self.client.get("/api/v3/organizations/test-organization/projects/training29957/workflows/1/steps")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200) #'QuerySet' object has no attribute 'orderBy'
        self.assertEqual(len(content), 5)
        '''
        response = self.client.put("/api/v3/organizations/test-organization/projects/training29957/workflows/1/steps/5",
                                   content_type='application/json',
                                   data=json.dumps(	{"name":"Workflow update test"}))
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        '''
        response = self.client.get("/api/v3/organizations/test-organization/projects/training29957/workflows/1/steps/5")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['name'], 'Workflow update test')
        '''
        response = self.client.delete("/api/v3/organizations/test-organization/projects/training29957/workflows/1/steps/5")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content, 'deleted')
        '''
        response = self.client.get("/api/v3/organizations/test-organization/projects/training29957/workflows/1/steps")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200) #'QuerySet' object has no attribute 'orderBy'
        self.assertEqual(len(content), 4)
        '''
        response = self.client.delete("/api/v3/organizations/test-organization/projects/training29957/workflows/2")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content, 'deleted')

        response = self.client.get("/api/v3/organizations/test-organization/projects/training29957/workflows")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 1)

    def test_boardcell(self):
        logged_in = self.client.login(username="test", password = "test")
        self.assertTrue(logged_in)
        response = self.client.get("/api/v3/organizations/test-organization/projects/training29957/boardcell")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(content, "You don't have access to that Organization")

        logged_in = self.client.login(username="staff", password = "staff")
        self.assertTrue(logged_in)
        response = self.client.get("/api/v3/organizations/test-organization/projects/training29957/boardcell")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 4)

        response = self.client.post("/api/v3/organizations/test-organization/projects/training29957/boardcell",
                                   content_type='application/json',
                                   data=json.dumps(	{"label":"test cell"}))
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/api/v3/organizations/test-organization/projects/training29957/boardcell")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 5)

        response = self.client.get("/api/v3/organizations/test-organization/projects/training29957/boardcell/5")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['label'], 'test cell')

        response = self.client.put("/api/v3/organizations/test-organization/projects/training29957/boardcell/5",
                                   content_type='application/json',
                                   data=json.dumps(	{"label":"updated test cell"}))
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/api/v3/organizations/test-organization/projects/training29957/boardcell/5")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['label'], 'updated test cell')

        response = self.client.delete("/api/v3/organizations/test-organization/projects/training29957/boardcell/5")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content, 'deleted')

        response = self.client.get("/api/v3/organizations/test-organization/projects/training29957/boardcell")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 4)

    def test_kanban_board(self):
        logged_in = self.client.login(username="test", password = "test")
        self.assertTrue(logged_in)
        response = self.client.get("/api/v3/organizations/test-organization/projects/training29957/boardutil/templates")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(content, "You don't have access to that Organization")

        logged_in = self.client.login(username="staff", password = "staff")
        self.assertTrue(logged_in)
        response = self.client.get("/api/v3/organizations/test-organization/projects/training29957/boardutil/templates")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 0)
        '''
        response = self.client.post("/api/v3/organizations/test-organization/projects/training29957/boardutil/wizard",
                                   content_type='application/json',
                                   data=json.dumps({}))
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 500)

        response = self.client.get("/api/v3/organizations/test-organization/projects/training29957/boardutil/templates")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 1)
        '''

    def test_policy(self):
        logged_in = self.client.login(username="test", password = "test")
        self.assertTrue(logged_in)
        response = self.client.get("/api/v3/organizations/test-organization/projects/training29957/policy")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(content, "You don't have access to that Organization")

        logged_in = self.client.login(username="staff", password = "staff")
        self.assertTrue(logged_in)
        response = self.client.get("/api/v3/organizations/test-organization/projects/training29957/policy")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 0)
        '''
        response = self.client.post("/api/v3/organizations/test-organization/projects/training29957/policy",
                                   content_type='application/json',
                                   data=json.dumps({"name":"Test Policy"}))
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200) #NOT NULL constraint failed: v2_kanban_policy.related_value

        response = self.client.get("/api/v3/organizations/test-organization/projects/training29957/policy")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 1)

        response = self.client.get("/api/v3/organizations/test-organization/projects/training29957/policy/1")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['name'], 'Test Policy')

        response = self.client.put("/api/v3/organizations/test-organization/projects/training29957/policy/1",
                                   content_type='application/json',
                                   data=json.dumps({"name":"Updated Test Policy"}))
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/api/v3/organizations/test-organization/projects/training29957/policy/1")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['name'], 'Updated Test Policy')

        response = self.client.delete("/api/v3/organizations/test-organization/projects/training29957/policy/1")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content, 'deleted')
        '''

    def test_board_header(self):
        logged_in = self.client.login(username="test", password = "test")
        self.assertTrue(logged_in)
        response = self.client.get("/api/v3/organizations/test-organization/projects/training29957/header")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(content, "You don't have access to that Organization")

        logged_in = self.client.login(username="staff", password = "staff")
        self.assertTrue(logged_in)
        response = self.client.get("/api/v3/organizations/test-organization/projects/training29957/header")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 0)
        '''
        response = self.client.post("/api/v3/organizations/test-organization/projects/training29957/header",
                                   content_type='application/json',
                                   data=json.dumps({"label":"Test board header"})) #missing input data
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/api/v3/organizations/test-organization/projects/training29957/header")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 0)

        response = self.client.get("/api/v3/organizations/test-organization/projects/training29957/header/1")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['label'], 'Test board header')

        response = self.client.put("/api/v3/organizations/test-organization/projects/training29957/header/1",
                                   content_type='application/json',
                                   data=json.dumps({"label":"Updated test board header"}))
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/api/v3/organizations/test-organization/projects/training29957/header/1")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['label'], 'Updated test board header')

        response = self.client.delete("/api/v3/organizations/test-organization/projects/training29957/header/1")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content, 'deleted')
        '''
