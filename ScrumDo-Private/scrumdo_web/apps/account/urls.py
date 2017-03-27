from django.conf.urls import patterns, url
from django.contrib.auth.views import logout
from apps.emailconfirmation.views import confirm_email
import views

urlpatterns = (
    url(r'^$', views.default, name='account_default'),
    url(r'^githubsignup/$', views.githubsignup, name="githubsignup"),
    url(r'^signup/$', views.SignUpView.as_view(), name="acct_signup"),
    url(r'^modal/signup/$', views.SignUpView.as_view(template_name="account/register_popup.html"), name="acct_signup_popup"),
    url(r'^signup/(?P<registration_key>.+)/$', views.SignUpConfirmation.as_view(), name="register_key"),
    url(r'^login/$', views.login, name="acct_login"),
    url(r'^login/openid/$', views.login, {'associate_openid': True}, name="acct_login_openid"),
    url(r'^password_reset/$', views.password_reset, name="acct_passwd_reset"),
    url(r'^logout/$', logout, {"template_name": "account/logout.html"}, name="acct_logout"),
    url(r'^confirm_email/(\w+)/$', confirm_email, name="acct_confirm_email"),
    url(r'^password_reset_key/(\w+)/$', views.password_reset_from_key, name="acct_passwd_reset_key"),
    url(r'^delete_account/$', views.delete_account, name="delete_account"),
)
