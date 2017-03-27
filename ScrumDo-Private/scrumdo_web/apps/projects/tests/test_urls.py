from django.test import TestCase
from django.conf import settings

# Basic set of tests that just hits all the configured urls and checks status code

import logging

logger = logging.getLogger(__name__)


class UrlsTest(TestCase):
    fixtures = ["sample_organization.json"]

    def _test_url(self, url, code=200):
        response = self.client.get(url)
        self.assertEqual(response.status_code, code, "%s failed to load status: %d" % (url, response.status_code))

    def test_urls(self):
        settings.ROLLBAR['access_token'] = ''
        settings.ROLLBAR['environment'] = ''

        logged_in = self.client.login(username="scrumdo", password="staff")
        self.assertTrue(logged_in)
        urls_302 = [
            "/account/githubsignup/",
            "/github/login",
            "/googleauth/loginredirect",
            "/projects/story_permalink/1",
            "/email/email_config",
            "/projects/training29957/reports",
            "/projects/test-project/iteration/5",
            "/projects/test-project/planning",
            "/projects/training29957/board",

            "/projects/epic_permalink/1",
            "/projects/project/test-project/",
            "/projects/project/test-project/activate/",
            "/projects/project/test-project/admin",
            "/slack/auth_callback/training29957",
            "/subscription/expired/test-organization/staff",
            "/subscription/free_plan/test-organization",
            "/projects/project/training29957/search",
            "/classic_picker",
        ]
        
        urls = [
            "/",
            "/orgs",
            "/404testing/",
            "/500testing/",
            "/about/changelog/",
            "/about/privacy/",
            "/about/terms/",
            "/account/",
            "/account/delete_account/",
            "/account/login/",
            "/account/login/openid/",
            "/account/password_reset/",
            "/api/v3/account/me",
            "/api/v3/docs",
            "/api/v3/organizations/",
            "/api/v3/organizations/test-organization/active_stories",
            "/api/v3/organizations/test-organization/classic/projects",
            "/api/v3/organizations/test-organization/extras/github/",
            "/api/v3/organizations/test-organization/me",
            "/api/v3/organizations/test-organization/my_stories",
            "/api/v3/organizations/test-organization/newsfeed/grouped/0/7/",
            "/api/v3/organizations/test-organization/projects/training29957/access/",
            "/api/v3/organizations/test-organization/projects/training29957/boardcell/",
            "/api/v3/organizations/test-organization/projects/training29957/epics/1/",
            "/api/v3/organizations/test-organization/projects/training29957/epics/",
            "/api/v3/organizations/test-organization/projects/training29957/header/",
            "/api/v3/organizations/test-organization/projects/training29957/iteration/5/milestoneassignment/",
            "/api/v3/organizations/test-organization/projects/training29957/iteration_stats/5/",
            "/api/v3/organizations/test-organization/projects/training29957/iteration_stats/",
            "/api/v3/organizations/test-organization/projects/training29957/iterations/5/burndown/",
            "/api/v3/organizations/test-organization/projects/training29957/iterations/5/epic/1/stories/",
            "/api/v3/organizations/test-organization/projects/training29957/iterations/5/search/",
            "/api/v3/organizations/test-organization/projects/training29957/iterations/5/stories/1/tasks/",
            "/api/v3/organizations/test-organization/projects/training29957/iterations/5/stories/1/",
            "/api/v3/organizations/test-organization/projects/training29957/iterations/5/stories/",
            "/api/v3/organizations/test-organization/projects/training29957/iterations/5/",
            "/api/v3/organizations/test-organization/projects/training29957/iterations/1,2/stories/",
            "/api/v3/organizations/test-organization/projects/training29957/iterations/1/stories/1/news/",
            "/api/v3/organizations/test-organization/projects/training29957/iterations/",
            "/api/v3/organizations/test-organization/projects/training29957/newsfeed/grouped/0/1/",
            "/api/v3/organizations/test-organization/projects/training29957/newsfeed/",
            "/api/v3/organizations/test-organization/projects/training29957/search/",
            "/api/v3/organizations/test-organization/projects/training29957/stories/1/externalattachment",
            "/api/v3/organizations/test-organization/projects/training29957/stories/1/links/",
            "/api/v3/organizations/test-organization/projects/training29957/stories/1/news/",
            "/api/v3/organizations/test-organization/projects/training29957/stories/3/tasks/1/",
            "/api/v3/organizations/test-organization/projects/training29957/stories/1/tasks/",
            "/api/v3/organizations/test-organization/projects/training29957/stories/1/",
            "/api/v3/organizations/test-organization/projects/training29957/stories/epic/1/",
            "/api/v3/organizations/test-organization/projects/training29957/stories/links/",
            "/api/v3/organizations/test-organization/projects/training29957/stories/",
            "/api/v3/organizations/test-organization/projects/training29957/stories/",
            "/api/v3/organizations/test-organization/projects/training29957/storyqueue/",
            "/api/v3/organizations/test-organization/projects/training29957/time_entries/story/1/",
            "/api/v3/organizations/test-organization/projects/training29957/time_entries/?start=2015-01-01&end=2016-01-01",
            "/api/v3/organizations/test-organization/projects/training29957/workflows/",
            "/api/v3/organizations/test-organization/projects/training29957/",
            "/api/v3/organizations/test-organization/projects/",
            "/api/v3/organizations/test-organization/releasestats/",
            "/api/v3/organizations/test-organization/search/",
            "/api/v3/organizations/test-organization/subscription/",
            "/api/v3/organizations/test-organization/teams",
            "/api/v3/organizations/test-organization/time_entries/?start=2015-01-01&end=2016-01-01",
            "/api/v3/organizations/test-organization/users",
            "/api/v3/organizations/test-organization/",
            "/api/v3/organizations/subscription/",
            "/api/v3/query/",
            "/api/v3/resources/resources.json",
            "/avatar/avatar/32/",
            "/avatar/avatar/32/staff",
            "/avatar/defaultavatar/32/staff",
            "/github/log/training29957",
            "/github/login_associate_callback",
            "/github/login_callback",
            "/landing",
            "/landing/1",
            "/landing/2",
            "/landing/3",
            "/landing/4",
            "/organization/test-organization/dashboard",
            "/organization/test-organization/dashboard",
            "/organization/test-organization/edit",
            "/organization/test-organization/export",
            "/organization/test-organization/getscrumban",
            "/organization/test-organization/planning",
            "/organization/test-organization/tracktime",
            "/plans",
            "/projects/test-organization/training29957/tips",
            "/projects/test-organization/tips",
            "/projects/training29957/debug/rewind",
            "/projects/training29957/milestones",
            "/projects/training29957/storyqueue",
            "/projects/org/test-organization/search",
            "/projects/project/test-project/5/burndown",
            "/projects/project/test-project/burndown",
            "/projects/project/test-organization/create",
            "/projects/project/test-organization/create/personal",
            "/projects/project/test-project/project_prediction",
            "/projects/user/staff",
            "/realtime/training29957/chat_callback",
            "/realtime/training29957/chat_history",
            "/robots.txt",
            "/staff/",
            "/staff/kanbanstats",
            "/staff/recentstats",
            "/staff/scrumstats",
            "/staff/stats",
            "/staff/stats_data",
            "/staff/subscribers",
            "/staff/trialusers",
            "/staticurl",
            "/status",
            "/subscription/test-organization",
            "/subscription/test-organization/premium",
            "/subscription/expired/test-organization",
            "/subscription/register",
            "/subscription/retarget_org",
            ]

        for url in urls_302:
            self._test_url(url, 302)

        for url in urls:
            self._test_url(url)
