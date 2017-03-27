import logging

from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User

from apps.projects.models import Project

logger = logging.getLogger(__name__)


class BaseMixinTest(TestCase):
    fixtures = ["sample_organization.json"]

    def auth_login(self, username, password):
        self.logged_in = self.client.login(username=username, password=password)

    def init_user(self, username):
        self.user = User.objects.get(username=username)

    def switch_user(self, username):
        self.user = User.objects.get(username=username)

    def init_project(self, name):
        self.project = Project.objects.get(name=name) 

    def setUp(self):
        settings.ROLLBAR['access_token'] = ''
        settings.ROLLBAR['environment'] = ''


class StaffMixinTest(BaseMixinTest):
    
    def setUp(self):
        super(StaffMixinTest, self).setUp()
        self.init_user(username='staff')
        self.password = 'staff'
        self.auth_login(username=self.user.username, password=self.password)