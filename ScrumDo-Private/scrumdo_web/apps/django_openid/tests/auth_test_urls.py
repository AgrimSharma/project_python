from django.conf.urls import patterns, url
from django.http import HttpResponse
from apps.django_openid.registration import RegistrationConsumer

urlpatterns = patterns('',
    url(r'^$', lambda r: HttpResponse('Index')),
    url(r'^openid/(.*)', RegistrationConsumer()),
)
