from django.test import TestCase
from django.conf import settings

import json

# TODO: UploadAvatarHandler, AccountTokenHandler, EmailConfirmationHandler, ChangePasswordHandler,
#       DeleteAccountHandler, ApplicationAccountHandler, ApplicationTokenHandler, OpenIDTokenHandler



class AccountSettingsAPITest(TestCase):
    fixtures = ["projects_auth.json"]

    def setUp(self):
        settings.ROLLBAR['access_token'] = ''
        settings.ROLLBAR['environment'] = ''
        logged_in = self.client.login(username="tester", password="tester")
        self.assertTrue(logged_in)

    # def test_create_oauth_token(self):
    #     logged_in = self.client.login(username="tester", password="tester")
    #     self.assertTrue(logged_in)
    #
    #     response = self.client.post("/api/v3/account/token",
    #                                 content_type='application/json',
    #                                 data=json.dumps({'key':'xxx'}))
    #     import pdb
    #     pdb.set_trace()
    #     content = json.loads(response.content)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(content['key'], 'xxx')


    def test_me(self):
        response = self.client.get("/api/v3/account/me")
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content['username'], 'tester')
        self.assertEqual(content['first_name'], 'Test')

        response = self.client.post("/api/v3/account/me",
                                    content_type='application/json',
                                    data=json.dumps({'key':'xxx'}))
        self.assertEqual(response.status_code, 405)

        response = self.client.put("/api/v3/account/me",
                                    content_type='application/json',
                                    data=json.dumps({'first_name':'Marc', 'last_name':'Hughes'}))
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/api/v3/account/me")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['first_name'], 'Marc')
        self.assertEqual(content['last_name'], 'Hughes')

    def test_email_subscriptions(self):
        response = self.client.get("/api/v3/account/email_subscriptions")
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content, {'iteration_summary': 0, 'story_task': 0, 'mention': 2, 'marketing': True, 'epic': 0, 'digest': 0 , 'project_events':1})

        response = self.client.post("/api/v3/account/email_subscriptions",
                                    content_type='application/json',
                                    data=json.dumps({'key':'xxx'}))
        self.assertEqual(response.status_code, 405)


        content['iteration_summary'] = 1
        content['story_task'] = 2
        content['mention'] = 1
        content['marketing'] = False
        content['epic'] = 1
        content['digest'] = 1
        content['project_events'] = 2
        response = self.client.put("/api/v3/account/email_subscriptions",
                                    content_type='application/json',
                                    data=json.dumps(content))
        content2 = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content2, content)

        response = self.client.get("/api/v3/account/email_subscriptions")
        self.assertEqual(response.status_code, 200)
        content2 = json.loads(response.content)
        self.assertEqual(content2, content)

    def test_mail_confirm(self):
        response = self.client.post("/api/v3/account/email",
                                    content_type='application/json',
                                    data=json.dumps({'email':'aaaa'}))
        content = json.loads(response.content)
        self.assertEqual(response.status_code,200)
        self.assertEqual(content, "Email not valid!")

        response = self.client.post("/api/v3/account/email",
                                    content_type='application/json',
                                    data=json.dumps({'email':'aaaa@bb.gg'}))
        content = json.loads(response.content)
        self.assertEqual(response.status_code,200)

        response = self.client.get("/api/v3/account/email")
        content = json.loads(response.content)
        self.assertEqual(response.status_code,200)
        self.assertEqual(content['email'], 'aaaa@bb.gg')

        #--------------------------------------------start confirm

        # response = self.client.post("/api/v3/account/confirmemail/email",
        #                             content_type='application/json',
        #                             data=json.dumps({'email':'aaaa'}))
        #
        # self.assertEqual(response.status_code,200)
        #
        # content = json.loads(response.content)
        # print  "content post confirm %s" %content
        #
        # salt = sha_constructor(str(random())).hexdigest()[:5]
        # confirmation_key = sha_constructor(salt + 'aaaa').hexdigest()
        # confirmation_key = confirmation_key.lower()
        # email_address = EmailConfirmation.objects.confirm_email(confirmation_key)
        #
        #
        # response = self.client.get("/api/v3/account/email")
        # self.assertEqual(response.status_code,200)
        #
        # content = json.loads(response.content)
        # self.assertEqual(content['email'], 'aaaa')
        # print  "content get %s" %content
        #--------------------------------------- end confirm

        response = self.client.post("/api/v3/account/email",
                                    content_type='application/json',
                                    data=json.dumps({'email':'bbbb@ss.aa'}))

        self.assertEqual(response.status_code,200)

        response = self.client.get("/api/v3/account/email")
        content = json.loads(response.content)
        self.assertEqual(response.status_code,200)
        self.assertEqual(content['email'], 'bbbb@ss.aa')

        response = self.client.put("/api/v3/account/email",
                                   content_type='application/json',
                                    data=json.dumps({'email':'cccc@qq.pp'}))
        self.assertEqual(response.status_code, 405)

    def test_change_password(self):

        response = self.client.get("/api/v3/account/getpassword")
        self.assertEqual(response.status_code, 405)

        response = self.client.put("/api/v3/account/getpassword",
                                    content_type='application/json',
                                    data=json.dumps({"oldpassword":"tester","password1":"w2","password2":"w2"}))
        self.assertEqual(response.status_code, 405)

        response = self.client.post("/api/v3/account/getpassword",
                                    content_type='application/json',
                                    data=json.dumps({"oldpassword":"wrongpass","password1":"w2","password2":"w2"}))
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content, 'Password not set')

        response = self.client.post("/api/v3/account/getpassword",
                                    content_type='application/json',
                                    data=json.dumps({"oldpassword":"tester","password1":"","password2":""}))
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content, 'Password not set')

        response = self.client.post("/api/v3/account/getpassword",
                                    content_type='application/json',
                                    data=json.dumps({"oldpassword":"tester","password1":"12","password2":""}))
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content, 'Password not set')

        response = self.client.post("/api/v3/account/getpassword",
                                    content_type='application/json',
                                    data=json.dumps({"oldpassword":"tester","password1":"","password2":"12"}))
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content, 'Password not set')

        response = self.client.post("/api/v3/account/getpassword",
                                    content_type='application/json',
                                    data=json.dumps({"oldpassword":"tester","password1":"11","password2":"12"}))
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content, 'Password not set')

        response = self.client.post("/api/v3/account/getpassword",
                                    content_type='application/json',
                                    data=json.dumps({"oldpassword":"tester","password1":"w2","password2":"w2"}))
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content, 'Password Set Successfully')

        logged_in = self.client.logout()

        logged_in = self.client.login(username="tester", password="tester")
        self.assertFalse(logged_in)

        logged_in = self.client.login(username="tester", password="w2")
        self.assertTrue(logged_in)

    def test_oauthapp(self):
        response = self.client.put("/api/v3/account/OAuthApp",
                                    content_type='application/json',
                                    data=json.dumps({'name':'xxx','description':'qqq'}))
        self.assertEqual(response.status_code, 405)

        response = self.client.get("/api/v3/account/OAuthApp")
        self.assertEqual(response.status_code, 200)

        response = self.client.post("/api/v3/account/addOAuthApp",
                                    content_type='application/json',
                                    data=json.dumps({'name':'xxx','description':'qqq'}))
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)

    def test_openids(self):
        response = self.client.put("/api/v3/account/OpenID",
                                   content_type='application/json',
                                   data=json.dumps({'openid':'2'}))
        self.assertEqual(response.status_code, 405)

        response = self.client.get("/api/v3/account/OpenID")
        self.assertEqual(response.status_code, 200)

    '''
        response = self.client.post("/api/v3/account/OpenID",
                                   content_type='application/json',
                                   data=json.dumps({'openid':''}))
        self.assertEqual(response.status_code, 200)
    '''

    def test_oauthtokken(self):
        response = self.client.put("/api/v3/account/OAuthToken",
                                   content_type='application/json',
                                   data=json.dumps({'key':'12'}))
        self.assertEqual(response.status_code, 405)

        response = self.client.get("/api/v3/account/OAuthToken")
        self.assertEqual(response.status_code, 200)

        '''
        response = self.client.post("/api/v3/account/OAuthToken",
                                   content_type='application/json',
                                   data=json.dumps({}))
        self.assertEqual(response.status_code, 200)
        '''

    def test_delete_account(self):
        response = self.client.get("/api/v3/account/deleteaccount")
        self.assertEqual(response.status_code, 405)

        response = self.client.put("/api/v3/account/deleteaccount",
                                   content_type='application/json',
                                   data=json.dumps({'password':'tester'}))
        self.assertEqual(response.status_code, 405)

        response = self.client.post("/api/v3/account/deleteaccount",
                                   content_type='application/json',
                                   data=json.dumps({'password':'eee'}))
        self.assertEqual(response.status_code, 403)

        response = self.client.post("/api/v3/account/deleteaccount",
                                   content_type='application/json',
                                   data=json.dumps({'password':'tester'}))
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content, 'account deleted')

    def test_avatar(self):
        response = self.client.put("/api/v3/account/defaultavatar/avatar",
                                   content_type='application/json',
                                   data=json.dumps({}))
        self.assertEqual(response.status_code, 405)

        response = self.client.get("/api/v3/account/avatar")
        self.assertEqual(response.status_code, 200)

        response = self.client.post("/api/v3/account/deleteavatar/avatar",
                                   content_type='application/json',
                                   data=json.dumps({}))
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content, 'Avatar successfully deleted')

        '''
        response = self.client.post("/api/v3/account/defaultavatar/avatar",
                                   content_type='application/json',
                                   data=json.dumps({}))
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content, 'Avatar Upload Successful')
        '''