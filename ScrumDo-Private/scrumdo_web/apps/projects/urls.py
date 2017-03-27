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


from django.conf.urls import patterns, url, include
import views
import search_views
import iteration_views
import story_views
import time_views

urlpatterns = (
    url(r'^', include('apps.kanban.urls')),
    url(r'^user/(?P<username>[-\w]+)$', views.user_details_staff, name="user_details"),
    url(r'^user_by_email/(?P<email>.+)$', views.user_details_by_email, name="user_details_by_email"),
    url(r'^(?P<project_slug>[-\w]+)/milestones', views.milestones, name="milestones"),
    url(r'^(?P<project_slug>[-\w]+)/storyqueue', views.story_queue, name="story_queue"),
    url(r'^(?P<group_slug>[-\w]+)/planning$',views.planning, name="planning_tool"),
    url(r'^(?P<organization_slug>[-\w]+)/tips', views.project_tips, name="project_tips"),
    url(r'^(?P<organization_slug>[-\w]+)/(?P<project_slug>[-\w]+)/tips', views.project_tips, name="project_tips"),
    url(r'^project/(?P<group_slug>[-\w]+)/create$', views.create, name="project_create"),
    url(r'^project/(?P<group_slug>[-\w]+)/create/personal$', views.create, name="project_create_personal",  kwargs={'project_type': 'personal'}),
    url(r'^project/(?P<group_slug>[-\w]+)/$', views.project_detail_picker, name="project_detail"),
    url(r'^project/(?P<group_slug>[-\w]+)/activate/$', views.activate, name="project_activate"),
    url(r'^project/(?P<group_slug>[-\w]+)/activate/portfolio/$', views.activate_portfolio, name="portfolio_activate"),
    url(r'^project/(?P<group_slug>[-\w]+)/activate/(?P<remove_from_portfolio>[-\w]+)/$', views.activate, name="project_activate"),
    url(r'^project/(?P<group_slug>[-\w]+)/delete/$', views.delete, name="project_delete"),
    url(r'^project/(?P<group_slug>[-\w]+)/admin$', views.project_admin, name="project_admin"),
    url(r'^project/(?P<group_slug>[-\w]+)/(?P<iteration_id>[0-9]+)/burndown$', views.iteration_burndown),
    url(r'^project/(?P<group_slug>[-\w]+)/burndown$', views.project_burndown),
    url(r'^project/(?P<group_slug>[-\w]+)/project_prediction$', views.project_prediction, name="project_prediction"),


    url(r'^download/(?P<job_id>[0-9]+)$', views.file_job_download, name="file_job_download"),
    url(r'^download_file/(?P<job_id>[0-9]+)$', views.file_job_download_file, name="file_job_download_file"),
    url(r'^wait/(?P<job_id>[0-9]+)$', views.wait_job, name="wait_job"),
    url(r'^(?P<project_slug>[-\w]+)/$', views.project_app, name="project_app"),
)

urlpatterns += (
    url(r'^project/(?P<project_slug>[-\w]+)/search$', search_views.search_project, name="search_project"),
    url(r'^org/(?P<organization_slug>[-\w]+)/search$', search_views.search_organization, name="organization_search"),
)


urlpatterns += (
    url(r'^(?P<group_slug>[-\w]+)/iteration/(?P<iteration_id>[0-9]+)/import$', iteration_views.iteration_import, name="iteration_import"),
    url(r'^(?P<group_slug>[-\w]+)/iteration/(?P<iteration_id>[0-9]+)$', iteration_views.iteration, name="iteration"),
)

urlpatterns += (
    url(r'^story_permalink/(?P<story_id>[0-9]+)$', story_views.story_permalink, name="story_permalink"),
    url(r'^epic_permalink/(?P<epic_id>[0-9]+)$', story_views.epic_permalink, name="epic_permalink"),
)

urlpatterns += (
    url(r'^export_time/(?P<organization_slug>[-\w]+)$', time_views.export_time, name="export_time"),
)


