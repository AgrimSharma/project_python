import logging

from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from apps.account.models import RegistrationKey
from apps.organizations.models import Organization

from apps.organizations.mixins  import OrganizationMixin

logger = logging.getLogger(__name__)

URLS = {
    'signup': reverse('acct_signup'),
}

   
class AccountTest(TestCase):
    fixtures = ['subscription.json']

    def setUp(self):
        settings.ROLLBAR['access_token'] = ''
        settings.ROLLBAR['environment'] = ''
        
        self.data = {
            'email': 'test@mail.com',
            'username': 'testuser',
            'fullname': 'scrumdo test',
            'company': 'scrumdo',
            'password': 'password'
        }
        self.key = RegistrationKey.objects.create(email=self.data['email'])

    def test_registration(self):
        response = self.client.get(URLS['signup'])
        self.assertEqual(response.status_code, 200)

    def test_create_registration_key(self):
        response = self.client.post(URLS['signup'], self.data)
        self.assertTrue(response.context['is_registered'])
        self.assertEqual(response.status_code, 200)

    def test_registration_key(self):
        response = self.client.get(reverse('register_key', kwargs={'registration_key': self.key.key }))
        self.assertEqual(response.status_code, 200)

    def test_registration_url(self):
        response = self.client.post(reverse('register_key', kwargs={'registration_key': self.key.key }), self.data)
        user = response.context['user']
        organization = Organization.objects.all()
        self.assertTrue(user.is_authenticated())
        self.assertEqual(organization.count(), 1)
        self.assertEqual(organization[0].name, self.data['company'])
        self.assertEqual(user.username, self.data['username'])
        self.assertEqual(response.status_code, 302)
