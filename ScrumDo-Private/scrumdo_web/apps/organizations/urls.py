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

from django.conf.urls import url

import views
import team_views


urlpatterns = (
    url(r'^(?P<organization_slug>[-\w]+)/tracktime', views.track_time, name="track_time"),
    url(r'^(?P<organization_slug>[-\w]+)/planning$', views.organization_planning, name="organization_planning"),
    url(r'^(?P<organization_slug>[-\w]+)/dashboard$', views.organization_dashboard, name="organization_detail"),
    url(r'^(?P<organization_slug>[-\w]+)/dashboard$', views.organization_dashboard, name="organization_dashboard"),
    url(r'^(?P<organization_slug>[-\w]+)/redirect$', views.organization_redirect_to, name="organization_redirect"),
    url(r'^(?P<organization_slug>[-\w]+)/edit$', views.organization_edit, name="organization_edit"),
    url(r'^(?P<organization_slug>[-\w]+)/delete/$', views.organization_delete, name="organization_delete"),
    url(r'^(?P<organization_slug>[-\w]+)/extras', views.organization_extras, name="organization_extras"),
    url(r'^(?P<organization_slug>[-\w]+)/export$', views.export_organization, name="export_organization"),
    url(r'^(?P<organization_slug>[-\w]+)/getscrumban$', views.play_getscrumban_game, name="play_getscrumban_game")
)


urlpatterns += (
    url(r'^accept/currentuser/(?P<key>[-\w]+)$', team_views.logged_in_team_invite_accept, name="logged_in_team_invite_accept"),
    url(r'^accept/(?P<key>[-\w]+)$', team_views.team_invite_accept, name="team_invite_accept")
)
