API Reference
=============

The API in the project is realized with **django-piston**, which is out of support for a while.

.. note::
	It will be good to migrate to Django-REST-Framework (http://www.django-rest-framework.org), it has more support and features.
Every API call is done with creating a resource that is an implementation of Handlers class, those classes are split by files as follow.
The accepted HTTP requests are defined in the member **allowed_methods**; The fields that are expected are defined in the member **fields** in every class handler.

Pistons class function that represent the coresponding HTTP request are related as follows: 
1. HTTP POST -> create()
2. HTTP GET -> read()
#. HTTP PUT -> update()

Account settings
****************
This grouping is about the APIHandlers that are responsible for the Account operations: AccountTokenHandler_, AccountSettingsHandler_, EmailSubscriptionHandler_, ChangePasswordHandler_, DeleteAccountHandler_, ApplicationAccountHandler_, ApplicationTokenHandler_, OpenIDTokenHandler_

File location: apps/api_v2/handlers/accountsettings.py

AccountTokenHandler
-------------------

The functionality of this class is to verify the OAuth Token.

.. code-block:: python

	class AccountTokenHandler(BaseHandler):
	    allowed_methods = ('POST', )
	    fields = ('key',)

	    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
	    def create(self, request):
	        consumer = Consumer.objects.get(key=request.data.get("consumer"))
	        try:
	            token = OAuthToken.objects.get(user=request.user, consumer=consumer, token_type=2, is_approved=True)
	        except OAuthToken.DoesNotExist:
	            token = OAuthToken.objects.create_token(consumer, 2, long(time.time()), request.user)
	            token.is_approved = True
	            token.save()
	        return token

AccountSettingsHandler
----------------------

The functionality of this handler is to update the first_name and last_name values.

.. code-block:: python

	class AccountSettingsHandler(BaseHandler):
	    """
	    This handler retrieves and returns the "user" object used on the account settings page.
	    """
	    allowed_methods = ('GET', 'PUT')
	    fields = ('id', 'username', 'first_name', 'last_name', 'email', 'subscriptions')

	    @staticmethod
	    def subscriptions(user):
	        return _getUserOptions(user)


	    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
	    def update(self, request):
	        data = request.data
	        if "first_name" in data:
	            request.user.first_name = data['first_name']
	        if "last_name" in data:
	            request.user.last_name = data['last_name']
	        request.user.save()
	        return request.user


EmailSubscriptionHandler
------------------------

This handler maintains the Email subscriptions.

.. code-block:: python

	class EmailSubscriptionHandler(BaseHandler):
	    allowed_methods = ('GET', 'PUT')
	    model = EmailOptions
	    fields = ('story_task', 'epic', 'digest', 'iteration_summary', 'mention', 'marketing')

	    # From new -> classic we have fewer options for email subscriptions.
	    # this map defines what we call it in the new site to what fields it maps to in the classic
	    write_map = {
	        'story_task': ['story_assigned', 'story_status', 'story_edited', 'story_created',
	                       'story_deleted', 'story_comment', 'task_created', 'task_edited',
	                       'task_deleted', 'task_status'],
	        'epic': ['epic_created', 'epic_edited', 'epic_deleted'],
	        'digest': ['digest'],
	        'iteration_summary': ['iteration_summary'],
	        'mention': ['mention'],
	        'marketing': ['marketing']
	    }

	    @staticmethod
	    def story_task(option):
	        return option.story_edited

	    @staticmethod
	    def epic(option):
	        return option.epic_edited


	    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
	    def update(self, request):
	        data = request.data
	        options = _getUserOptions(request.user)
	        for inputKey in EmailSubscriptionHandler.write_map:
	            if inputKey in data:
	                for destinationField in EmailSubscriptionHandler.write_map[inputKey]:
	                    setattr(options, destinationField, data[inputKey])
	        options.save()
	        return options


	    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
	    def read(self, request):
	        return _getUserOptions(request.user)



UploadAvatarHandler
-------------------

This handler is used in the account settings page and handles uploading an avatar, hoosing a default avatar and deleting an avatar

.. code-block:: python
	
	class UploadAvatarHandler(BaseHandler):
	    allowed_methods = ('GET', 'POST')
	    fields = ('id', 'avatar', 'primary')
	    model = Avatar

	    def read(self, request):
	        """
	        This method finds and returns all avatars associated with a particular user_id
	        """
	        try:
	            return Avatar.objects.get(user=request.user, primary=True)
	        except Avatar.DoesNotExist:
	            return {}

	    def create(self, request, action=None):
	        """
	        This method calls two different functions depending on the action the user selects
	        """
	        user = request.user
	        data = request.data

	        if action == 'defaultavatar':
	            return self.defaultAvatar(request, user, data)

	        if action == 'deleteavatar':
	            return self.deleteAvatar(request, data)


	    def defaultAvatar(self, request, user, data):
	        path = avatar_file_path(user=user, filename=request.FILES['file'].name)
	        avatar = Avatar(user=user,
	                        primary=True,
	                        avatar=path,)
	        avatar.avatar.storage.save(path, request.FILES['file'])
	        avatar.save()
	        Avatar.objects.filter(user=user).exclude(id=avatar.id).delete()  # remove others
	        return "Avatar Upload Successful"

	    def deleteAvatar(self, request, data):
	        """
	        This method deletes a users avatar
	        """
	        Avatar.objects.filter(user=request.user).delete()
	        return "Avatar successfully deleted"


EmailConfirmationHandler
------------------------

This handler deals with all the email related functionality in the account settings page.


.. code-block:: python

	class EmailConfirmationHandler(BaseHandler):
	    model = EmailAddress
	    allowed_methods = ('GET', 'POST',)
	    fields = ("id", "user_id", "email", "verified", "primary")
	    write_fields = ("email", "verified")


	    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
	    def read(self, request):
	        """
	        This method finds and returns the EmailAddress object associated with the user_id
	        """
	        user = request.user
	        try:
	            return EmailAddress.objects.get(user=user, primary=True)
	        except EmailAddress.DoesNotExist:
	            logger.warn("Please add an Email to be associated with your ScrumDo account")
	            return "Please add an Email to be associated with your ScrumDo account"

	    @throttle(WRITE_THROTTLE_REQUESTS,THROTTLE_TIME, 'user_writes')
	    def create(self, request, action = None):
	        data = request.data
	        user = request.user

	        if action == 'changeemail':
	            return self.changeEmail(request, data)

	        if action == 'confirmemail':
	            return self.confirmEmail(request, data)

	        return self.changeEmail(request, data)

	    def changeEmail(self, request ,data):
	        try:
	            validate_email(data['email'])
	        except ValidationError as e:
	            return "Email not valid!"
	        else:
	            EmailAddress.objects.filter(user=request.user).delete()
	            address = EmailAddress(user=request.user, primary=True)
	            address.email = data['email']
	            address.verified = False
	            address.save()

	            request.user.email = data['email']
	            request.user.save()

	            EmailConfirmation.objects.send_confirmation(address)
	            return address

	    def confirmEmail(self, request, data):
	        if data == {}:
	            logger.warn("Please add an Email to be associated with your ScrumDo account")
	            return "Please add an Email to be associated with your ScrumDo account"

	        email_address = EmailAddress.objects.get(user=request.user, primary=True, verified=False)
	        confirmation = EmailConfirmation.objects.send_confirmation(email_address)
	        return confirmation


ChangePasswordHandler
---------------------

This handler deals with the password change requests.


.. code-block:: python

	class ChangePasswordHandler(BaseHandler):
	    allowed_methods = ('POST',)
	    fields = ()
	    model = ChangePasswordForm

	    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
	    def create(self, request):
	        password_change_form = ChangePasswordForm(request.user, request.data)
	        if password_change_form.is_valid():
	            password_change_form.save()
	            return "Password Set Successfully"
	        return "Password not set"


DeleteAccountHandler
--------------------

This handler deals with the account deletion requests.


.. code-block:: python

	class DeleteAccountHandler(BaseHandler):
	    allowed_methods = ('POST',)

	    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
	    def create(self, request):

	        if not request.user.check_password(request.data['password']):
	            raise PermissionDenied()

	        if Organization.objects.filter(creator=request.user).count() == 0:
	            request.user.is_active = False
	            request.user.email = ''
	            request.user.save()

	            for password_reset in PasswordReset.objects.filter(user=request.user):
	                password_reset.delete()

	            for task in Task.objects.filter(assignee=request.user):
	                task.assignee = None
	                task.save()


	            for email_subscription in EmailOptions.objects.filter(user=request.user):
	                email_subscription.delete()

	            for user_openid in UserOpenidAssociation.objects.filter(user=request.user):
	                user_openid.delete()
	            return "account deleted"

	        else:
	            return "You need to delete your organizations before you delete your account"

	        return "Please re-enter password"


ApplicationAccountHandler
-------------------------

Consumer ?? UNKNOWN MEANING


.. code-block:: python

	class ApplicationAccountHandler(BaseHandler):
	    allowed_methods = ('GET', 'POST')
	    fields = ('id', 'name', 'key', 'description', 'secret')
	    model = ConsumerForm

	    def read(self, request):
	        existing_apps = Consumer.objects.filter(user=request.user)
	        return existing_apps

	    def create(self, request):
	        form = ConsumerForm(request.data)
	        if form.is_valid():
	            consumer = form.save(commit=False)
	            consumer.user = request.user
	            consumer.status = 1
	            consumer.generate_random_codes()
	            return consumer
	        return False



ApplicationTokenHandler
-----------------------

This handler is related on checking Application credentials (unknown meaning)

.. code-block:: python

	class ApplicationTokenHandler(BaseHandler):
	    allowed_methods = ('GET', 'POST')
	    fields = ('id', 'key', 'consumer')
	    model = OAuthToken

	    def read(self, request):
	        oauth_keys = OAuthToken.objects.filter(user=request.user)
	        return oauth_keys

	    def create(self, request):
	        data = request.data
	        key = OAuthToken.objects.get(key=data['key'], user=request.user)
	        appname = key.consumer.name
	        key.delete()
	        return "Successfully deleted developer key for %s application" % appname


OpenIDTokenHandler
------------------

Handler dealing with OpenID token authentication

.. code-block:: python

	class OpenIDTokenHandler(BaseHandler):
	    allowed_methods = ('GET', 'POST')
	    fields = ('id', 'user', 'user_id')

	    def read(self, request):
	        return request.user.openids

	    def create(self, request):
	        openID = request.user.openids.get(openid=request.data['openid'])
	        openID.delete()
	        return request.user.openids