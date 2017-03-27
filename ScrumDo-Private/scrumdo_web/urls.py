# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
#
# This software is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy (See file COPYING) of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

from django.conf.urls import include, patterns, url
from django.conf import settings
import views
import feeds

from django.views.generic import TemplateView, RedirectView

from apps.projects.views import home, classic_picker, test_page
from apps.subscription.views import plans
from apps.account.openid_consumer import PinaxConsumer
from apps.account.views import signup
from apps.subscription.retarget_views import retarget
from apps.attachments.views import attachment_redirect, note_attachment_redirect
from apps.kanban.views import shared_board, shared_project

from views import staticurl, betaOptions

from django.contrib import admin

admin.autodiscover()



urlpatterns = (
    url(r'^$', home, name="home"),
    url(r'^classic_picker$', classic_picker, name="classic_picker"),
    url(r'^test_page$', test_page, name="test_page"),
    url(r'^home$', RedirectView.as_view(url='https://www.scrumdo.com/')),
    url(r'^home2$', RedirectView.as_view(url='https://www.scrumdo.com/')),
    url(r'^beta$', betaOptions),
    url(r'^landing$',   TemplateView.as_view(template_name='landing/landing-picker.html')),
    url(r'^landing/1$', TemplateView.as_view(template_name='landing/try-scrumdo-now.html')),
    url(r'^landing/2$', TemplateView.as_view(template_name='landing/try-scrumdo-now2.html')),
    url(r'^landing/3$', TemplateView.as_view(template_name='landing/try-scrumdo-now3.html')),
    url(r'^landing/4$', TemplateView.as_view(template_name='landing/try-scrumdo-now4.html')),
    url(r'^favicon.ico', RedirectView.as_view(url='https://d1949u65ypatvu.cloudfront.net/static/v0/img/favicon/favicon.ico')),
    url(r'^plans$', plans, name="plans", kwargs={"template":"plans-b.html"}),
    url(r'^blog/', RedirectView.as_view(url='http://content.scrumdo.com/blog/')),
    url(r'^subscription/', include('apps.subscription.urls')),
    url(r'^email/', include('apps.email_notifications.urls')),
    url(r'^github/', include('apps.github_integration.urls')),
    url(r'^slack/', include('apps.slack.urls')),
    url(r'^flowdock/', include('apps.flowdock.urls')),
    url(r'^realtime/', include('apps.realtime.urls')),
    url(r'^orgs$', home , name="org_picker", kwargs={'force_org_view':False}),
    url(r'^robots.txt$', TemplateView.as_view(template_name='robots.txt')),
    url(r'^status$', views.status),
    url(r'^forum/', RedirectView.as_view(url=settings.SUPPORT_URL)),
    url(r'^feeds/project/(?P<project_id>[0-9]+)/(?P<project_key>.*)/$', feeds.ProjectStories() ),
    url(r'^feeds/project/(?P<project_id>[0-9]+)/(?P<project_key>.*)$', feeds.ProjectStories() ),
    url(r'^about/terms/$', TemplateView.as_view(template_name="about/tos.html"), name="terms"),
    url(r'^about/privacy/$', TemplateView.as_view(template_name="about/privacy.html"), name="privacy"),
    url(r'^about/changelog/$', TemplateView.as_view(template_name="about/changelog.html"), name="changelog"),
    url(r'^account/', include('apps.account.urls')),

    url(r'^openid/login/googleauth/', include('apps.google_auth.urls')),
    url(r'^googleauth/', include('apps.google_auth.urls')),


    url(r'^openid/(.*)', PinaxConsumer()),
    url(r'^avatar/', include('apps.avatar.urls')),
    url(r'^projects/', include('apps.projects.urls')),
    url(r'^inbox/', include('apps.inbox.urls')),
    url(r'^organization/', include('apps.organizations.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/v[23]/', include('apps.api_v2.urls')),
    url(r'^forms/', include('apps.form_designer.urls')),
    url(r'^staff/', include('apps.staff.urls')),
    url(r'^unsubscribe/', include('apps.unsubscribe.urls')),
    url(r'^uploader/', include('apps.uploader.urls')),
    url(r'^shared/project/(?P<share_key>[a-z0-9]+)', shared_project),
    url(r'^shared/(?P<share_key>[a-z0-9]+)', shared_board),
    url(r'^staticurl', staticurl),
    url(r'^attachment/(?P<attachment_id>[0-9]+)', attachment_redirect),
    url(r'^attachment/note/(?P<attachment_id>[0-9]+)', note_attachment_redirect),
    url(r'^404testing/$', TemplateView.as_view(template_name='404.html')),
    url(r'^500testing/$', TemplateView.as_view(template_name='500.html')),

    url(r'^incoming_email/', include('apps.incoming_email.urls')),

    url(r'^retarget/(?P<key>[a-zA-Z0-9]+)$', retarget),
)


if settings.SERVE_MEDIA:
    from django.contrib.staticfiles.views import serve as static_serve
    urlpatterns += (
        url(r'^static/(?P<path>.*)$', static_serve),
    )

# handler500 = handler404 = views.server_error
