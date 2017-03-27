from django.conf.urls import patterns, url
import views

urlpatterns = (
    url('^avatar/(?P<size>[0-9]+)/(?P<username>.*)/[0-9]+$', views.avatar_redirect, name='avatar_redirect'),
    url('^avatar/(?P<size>[0-9]+)/(?P<username>.*)$', views.avatar_redirect, name='avatar_redirect'),
    url('^avatar/(?P<size>[0-9]+)/$', views.avatar_redirect),
    url('^defaultavatar/(?P<size>[0-9]+)/(?P<username>.+)$', views.avatar_default, name='avatar_default'),
)
