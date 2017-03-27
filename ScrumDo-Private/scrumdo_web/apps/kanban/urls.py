from django.conf.urls import patterns, url
import views

urlpatterns = (
    url(r'^(?P<project_slug>[-\w]+)/board$', views.kanban_board, name="kanban_board"),
    url(r'^(?P<project_slug>[-\w]+)/reports$', views.kanban_reports, name="kanban_reports"),
    url(r'^(?P<project_slug>[-\w]+)/debug/rewind$', views.debug_rewind, name="debug_rewind"),
)
