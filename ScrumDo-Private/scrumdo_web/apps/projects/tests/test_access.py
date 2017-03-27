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

from apps.projects import portfolio_managers, access
from apps.projects import managers as project_managers
from apps.projects.org_backlog import set_project_parents
from apps.organizations.models import Organization, Team
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)
settings.ROLLBAR['access_token'] = ''
settings.ROLLBAR['environment'] = ''

class AccessTestCase(TestCase):
    fixtures = ["sample_organization.json"]

    def setUp(self):
        settings.ROLLBAR['access_token'] = ''
        settings.ROLLBAR['environment'] = ''

    def _create_portfolio_structure(self):
        logged_in = self.client.login(username="staff", password="staff")

        self.org = Organization.objects.get(slug='test-organization')
        self.user = User.objects.get(username='staff')
        self.portfolio = portfolio_managers.create_portfolio(self.org, 'Access Control Portfolio', self.user, 'Portfolio Epic', 'fa-folder')
        self.level1 = portfolio_managers.create_portfolio_level(self.portfolio, 'Programs', 1, 'fa-bullseye')
        self.level2 = portfolio_managers.create_portfolio_level(self.portfolio, 'Teams', 2, 'fa-users')
        
        self.programA = project_managers.create_project('Program A', self.org, self.user, False, [],
                                                              parent_ids=[self.portfolio.root.id],
                                                              work_item_name='Feature') 
        self.programB = project_managers.create_project('Program B', self.org, self.user, False, [],
                                                              parent_ids=[self.portfolio.root.id],
                                                              work_item_name='Feature') 
        self.teamProjectA = project_managers.create_project('Team A', self.org, self.user, False, [],
                                                              parent_ids=[self.programA.id],
                                                              work_item_name='Teams') 

        self.teamProjectB = project_managers.create_project('Team B', self.org, self.user, False, [],
                                                              parent_ids=[self.programB.id, self.programA.id],
                                                              work_item_name='Teams')   
        self.teamProjectC = project_managers.create_project('Team C', self.org, self.user, False, [],
                                                              parent_ids=[self.programB.id],
                                                              work_item_name='Teams')
        
        portfolio_managers.add_project_to_portfolio(self.level1, self.programA)
        portfolio_managers.add_project_to_portfolio(self.level1, self.programB)

        portfolio_managers.add_project_to_portfolio(self.level2, self.teamProjectA)
        portfolio_managers.add_project_to_portfolio(self.level2, self.teamProjectB)
        portfolio_managers.add_project_to_portfolio(self.level2, self.teamProjectC)

        #create Teams with different Access
        self.readTeam = Team(organization=self.org, name='Read Only Team', access_type='read')
        self.readTeam.save()
        self.writeTeam = Team(organization=self.org, name='Writer Team', access_type='write')
        self.writeTeam.save()
        self.adminTeam = Team(organization=self.org, name='Admin Team', access_type='admin')
        self.adminTeam.save()
        self.staffTeam = Team(organization=self.org, name='Staff Team', access_type='staff')
        self.staffTeam.save()
        
        #create users for different teams
        self.userReader = User.objects.create_user(username='readeruser', email='reader@scrumdo.com', password='reader')
        self.userWriter = User.objects.create_user(username='writeruser', email='readwriterer@scrumdo.com', password='writer')
        self.userAdmin = User.objects.create_user(username='adminuser', email='admin@scrumdo.com', password='admin')
        self.userStaff = User.objects.create_user(username='staffuser', email='staff@scrumdo.com', password='staff')

        #add users to teams
        self.readTeam.members.add(self.userReader)
        self.writeTeam.members.add(self.userWriter)
        self.adminTeam.members.add(self.userAdmin)
        self.staffTeam.members.add(self.userStaff)

    def test_porfolio_access(self):
        self._create_portfolio_structure()

        #test readonly access
        self.readTeam.projects.add(self.teamProjectA)
        self.assertEqual(access.has_read_access(self.teamProjectA, self.userReader), True)
        self.assertEqual(access.has_write_access(self.teamProjectA, self.userReader), False)
        self.assertEqual(access.has_read_access(self.teamProjectB, self.userReader), False)

        #user must have read access to parents projects
        self.assertEqual(access.has_read_access(self.programA, self.userReader), True)
        self.assertEqual(access.has_read_access(self.portfolio.root, self.userReader), True)

        # test read/write access
        self.writeTeam.projects.add(self.programA)
        self.assertEqual(access.has_write_access(self.programA, self.userWriter), True)
        self.assertEqual(access.has_admin_access(self.programA, self.userWriter), False)

        #user must have read/write access to its children
        self.assertEqual(access.has_write_access(self.teamProjectA, self.userWriter), True)
        self.assertEqual(access.has_write_access(self.teamProjectB, self.userWriter), True)

        #user must not have read/write access to its parents
        self.assertEqual(access.has_write_access(self.portfolio.root, self.userWriter), False)

        #test admin access
        self.adminTeam.projects.add(self.programB)
        self.assertEqual(access.has_admin_access(self.programB, self.userAdmin), True)
        self.assertEqual(access.has_admin_access(self.portfolio.root, self.userAdmin), False)
        self.assertEqual(access.has_admin_access(self.teamProjectB, self.userAdmin), True)
        self.assertEqual(access.has_admin_access(self.teamProjectC, self.userAdmin), True)

        #test staff access
        self.assertEqual(access.has_admin_access(self.programB, self.userStaff), True)
        self.assertEqual(access.has_admin_access(self.programA, self.userStaff), True)
        self.assertEqual(access.has_admin_access(self.teamProjectA, self.userStaff), True)
        self.assertEqual(access.has_admin_access(self.teamProjectB, self.userStaff), True)
        self.assertEqual(access.has_admin_access(self.teamProjectC, self.userStaff), True)
        
