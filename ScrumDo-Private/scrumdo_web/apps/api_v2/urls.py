from django.conf.urls import url, include
from django.http import HttpResponse
from handlers import *

import piston.authentication as authentication
from piston.authentication import NoAuthentication, HttpBasicAuthentication
from piston.resource import Resource
from auth import ScrumDoAuthentication
from django.views.decorators.cache import cache_control

from django.conf import settings
from cors_resource import CORSResource

import views
from apps.eventCalendar.views import events_calendar
auth = ScrumDoAuthentication(realm="ScrumDo API V3")
cached_resource = cache_control(public=False, maxage=0, s_maxage=0, no_cache=True, must_revalidate=True)


def create_resource(Handler):
    if settings.DEBUG:
        resource = cached_resource(CORSResource(Handler, authentication=auth))
    else:
        resource = cached_resource(Resource(Handler, authentication=auth))

    # See inside resource.py, we manually apply csrf to session based auth but allow OAuth and HTTP Basic
    resource.csrf_exempt = True

    return resource


basicAuth = HttpBasicAuthentication(realm='ScrumDo Access Token')


def nochallenge(self, request=None):
        resp = HttpResponse("Authorization Required")
        resp.status_code = 401
        return resp
basicAuth.challenge = nochallenge

account_token_handler = cached_resource(Resource(AccountTokenHandler, authentication=basicAuth))
account_token_handler.csrf_exempt = True

project_share_handler = create_resource(ProjectShareHandler)
account_settings_handler = create_resource(AccountSettingsHandler)
email_confirmation_handler = create_resource(EmailConfirmationHandler)
change_password_handler = create_resource(ChangePasswordHandler)
upload_avatar_handler = create_resource(UploadAvatarHandler)
delete_account_handler = create_resource(DeleteAccountHandler)
oauth_app_handler = create_resource(ApplicationAccountHandler)
oauth_token_handler = create_resource(ApplicationTokenHandler)
openid_app_handler = create_resource(OpenIDTokenHandler)
org_handler = create_resource(OrganizationHandler)
project_handler = create_resource(ProjectHandler)
dashboard_projects_handler = create_resource(DashbaordProjectsHandler)
project_access_handler = create_resource(ProjectAccessHandler)
iteration_handler = create_resource(IterationHandler)
iteration_sentiments_handler = create_resource(IterationSentimentsHandler)
sentiment_report_handler = create_resource(SentimentReportHandler)
current_iteration_handler = create_resource(CurrentIterationHandler)
story_handler = create_resource(StoryHandler)
mini_story_handler = create_resource(MiniStoryHandler)
story_assignment_handler = create_resource(StoryAssignmentHandler)
epic_handler = create_resource(EpicHandler)
epic_stats_handler = create_resource(EpicStatsHandler)
search_handler = create_resource(SearchHandler)
newsfeed_handler = create_resource(NewsfeedHandler)
story_newsfeed_handler = create_resource(StoryNewsFeedHandler)
task_handler = create_resource(TaskHandler)
burndown_handler = create_resource(BurndownHandler)
story_duplicate_handler = create_resource(DuplicateStoryHandler)
story_convert_epic_handler = create_resource(ConvertToEpicHandler)
story_order_handler = create_resource(StoryOrderHandler)
story_attr_handler = create_resource(StoryAttributesHandler)
board_attr_handler = create_resource(BoardAttributesHandler)
time_handler = create_resource(TimeEntryHandler)
story_aging_handler = create_resource(StoryAgingHandler)
story_blocker_handler = create_resource(StoryBlockerHandler)
cell_movement_handler = create_resource(CellMovementHandler)
point_scale_handler = create_resource(PointScaleHandler)
project_lead_time_handler = create_resource(ProjectLeadTimeHandler)
project_notes_handler = create_resource(NoteHandler)
notes_attachment_handler = create_resource(NoteAttachmentHandler)
notes_comments_handler = create_resource(NoteCommentHandler)
timeline_story_handler = create_resource(TimelineStoryHandler)

# current_stories_handler is now deprecated, don't use it for new things.
current_stories_handler = create_resource(CurrentStoriesHandler)

my_stories_handler = create_resource(MyStoryHandler)

offline_job_handler = create_resource(OfflineJobHandler)
job_handler = create_resource(JobHandler)
task_order_handler = create_resource(TaskOrderHandler)
project_members_handler = create_resource(ProjectMemberHandler)
story_comments_handler = create_resource(StoryCommentHandler)
story_dependencies_handler = create_resource(StoryDependencyHandler)
project_dependencies_handler = create_resource(ProjectDependencyHandler)
workflow_handler = create_resource(WorkflowHandler)
workflow_steps_handler = create_resource(WorkflowStepHandler)
boardcell_handler = create_resource(BoardCellHandler)
iteration_cell_counts_handler = create_resource(IterationCellCounts)
calendar_view_handler = create_resource(EventCalenderView)

kanbanstats_handler = create_resource(KanbanStatHandler)
policy_handler = create_resource(PolicyHandler)
board_graphic_handler = create_resource(BoardGraphicHandler)
attachment_handler = create_resource(AttachmentHandler)
attachment_cover_handler = create_resource(AttachmentCoverHandler)
release_handler = create_resource(ReleaseHandler)
release_stories_handler = create_resource(ReleaseStoriesHandler)
release_stories_stats_handler = create_resource(ReleaseStoriesStatsHandler)
release_teams_stats_handler = create_resource(ReleaseTeamsStatsHandler)
project_release_handler = create_resource(ProjectReleaseHandler)
move_story_handler = create_resource(MoveStoryHandler)
board_image_handler = create_resource(BoardImageHandler)
kanban_board_handler = create_resource(KanbanBoardHandler)
subscription_handler = create_resource(SubscriptionHandler)
subscription_code_handler = create_resource(SubscriptionCodeHandler)


header_handler = create_resource(BoardHeaderHandler)
query_handler = create_resource(SavedQueryHandler)
project_stats_handler = create_resource(ProjectStatsHandler)
project_kanban_stats_handler = create_resource(ProjectKanbanStatsHandler)
external_link_handler = create_resource(ExternalStoryMappingHandler)
portfolio_handler = create_resource(PortfolioHandler)
portfolio_build_handler = create_resource(PortfolioBuildHandler)
user_handler = create_resource(UserHandler)
grouped_newsfeed_handler = create_resource(GroupedNewsfeedHandler)
project_export_handler = create_resource(ProjectExportHandler)
team_handler = create_resource(TeamHandler)
project_team_handler = create_resource(ProjectTeamHandler)
iteration_stats_handler = create_resource(IterationStatsHandler)
all_users_handler = create_resource(AllUsersHandler)
favorites_handler = create_resource(FavoritesHandler)
classic_project_handler = create_resource(ClassicProjectHandler)
email_subscription_handler = create_resource(EmailSubscriptionHandler)
emailcard_handler = create_resource(EmailCardExtraHandler)
github_handler = create_resource(GithubExtraHandler)
github_user_handler = create_resource(GithubAccountHandler)

slack_handler = create_resource(SlackExtraHandler)
flowdock_handler = create_resource(FlowdockExtraHandler)
hipchat_handler = create_resource(HipChatExtraHandler)
story_queue_handler = create_resource(StoryQueueHandler)
label_handler = create_resource(LabelHandler)
tag_handler = create_resource(TagHandler)
milestone_assignment_handle = create_resource(MilestoneAssignmentHandler)
assignment_options_handler = create_resource(AssigmentOptionsHandler)

pull_request_handler = create_resource(PullRequestHandler)  # Not in a URL yet, but leave so we get the serialization.

release_stat_handler = create_resource(ReleaseStatHandler)
release_child_stat_handler = create_resource(ReleasesChildStatsHandler)
inbox_handler = create_resource(InboxGroupHandler)

saved_report_handler = create_resource(SavedReportHandler)
run_saved_report_handler = create_resource(RunSavedReportHandler)

program_increment_dependency_handler = create_resource(IncrementDependencyHandler)

program_increment_handler = create_resource(ProgramIncrementHandler)
program_increment_schedule_handler = create_resource(ProgramIncrementScheduleHandler)

wip_limit_handler = create_resource(WIPLimitHandler)

risks_handler = create_resource(RiskHandler)
risk_target_handler = create_resource(RiskTargetSearch)
pig_picture_stats_handler = create_resource(BigPictureStatsHandler)
system_risks_handler = create_resource(SystemRiskHandler)

# Anonymous calls
subscription_plan_handler = cached_resource(Resource(SubscriptionPlanHandler, authentication=NoAuthentication()))
shared_project_handler = cached_resource(Resource(SharedProjectHandler, authentication=NoAuthentication()))
shared_story_handler = cached_resource(Resource(SharedStoryHandler, authentication=NoAuthentication()))




# All project_urlpatterns get both an organization_slug and a project_slug passed in the url
# calendar_urlpatterns = [
# ]
project_urlpatterns = [
    url(r'^inbox/?$', inbox_handler),
    url(r'^inbox/(?P<groupId>[0-9]+)$', inbox_handler),
    url(r'^milestoneassignment/$', milestone_assignment_handle),
    url(r'^milestoneassignment/(?P<milestone_id>[0-9]+)$', milestone_assignment_handle),
    url(r'^iteration/(?P<iteration_id>[0-9]+)/milestoneassignment/$', milestone_assignment_handle),

    url(r'^increment/(?P<increment_id>[0-9]+)/assignments/?$', story_assignment_handler),
    url(r'^increment/(?P<increment_id>[0-9]+)/assignments/(?P<story_id>[0-9]+)/?$', story_assignment_handler),

    url(r'^increment/(?P<increment_id>[0-9]+)/?$', program_increment_handler),
    url(r'^increment/?$', program_increment_handler),
    url(r'^increment_by_iteration/(?P<iteration_id>[0-9]+)/?$', program_increment_handler),
    url(r'^increment/(?P<increment_id>[0-9]+)/schedule/?$', program_increment_schedule_handler),
    url(r'^increment/(?P<increment_id>[0-9]+)/schedule/(?P<schedule_id>[0-9]+)/?$', program_increment_schedule_handler),
    url(r'^extras/github/?$', github_handler),
    url(r'^extras/slack/?$', slack_handler),
    url(r'^extras/flowdock/?$', flowdock_handler),
    url(r'^extras/hipchat/?$', hipchat_handler),
    url(r'^extras/emailcard/?$', emailcard_handler),
    url(r'^labels/?$', label_handler),
    url(r'^labels/(?P<label_id>[0-9]+)?$', label_handler),
    url(r'^tags/?$', tag_handler),
    url(r'^tags/(?P<tag_id>[0-9]+)?$', tag_handler),
    url(r'^share/?$', project_share_handler),
    url(r'^share/(?P<share_id>[0-9]+)/?$', project_share_handler),

    # TODO - what is this next line for? Would match:
    # /api/vN/organizations/SLUG/projects/SLUG/projects
    url(r'^projects/?$', project_handler),

    url(r'^storyqueue/?$', story_queue_handler),
    url(r'^access/?$', project_access_handler),
    url(r'^stats/?$', project_stats_handler),
    url(r'^kanbanstats/?$', project_kanban_stats_handler),
    url(r'^newsfeed/grouped?/(?P<start_day>[0-9]+)/(?P<end_day>[0-9]+)/?', grouped_newsfeed_handler),
    url(r'^iterations/(?P<iteration_id>[0-9]+)/newsfeed/grouped?/(?P<start_day>[0-9]+)/(?P<end_day>[0-9]+)/?', grouped_newsfeed_handler),
    url(r'^newsfeed/?$', newsfeed_handler),
    url(r'^burndown/?$', burndown_handler),
    url(r'^export/?$', project_export_handler),
    url(r'^export/(?P<iteration_id>[0-9]+)?$', project_export_handler),
    url(r'^export/(?P<iteration_id>[0-9]+)/planning/(?P<team_slug>[-\w]+)?$', project_export_handler),
    url(r'^search/?$', search_handler),
    url(r'^iterations/(?P<iteration_id>[0-9,]+)/search/?$', search_handler),
    url(r'^members/?$', project_members_handler),
    url(r'^blockers/(?P<action>[-\w]+)/?$', story_blocker_handler),
    url(r'^stories/(?P<story_id>[0-9]+)/movements/?$', cell_movement_handler),
    url(r'^iteration/(?P<iteration_id>[0-9]+)/cell_counts/?$', iteration_cell_counts_handler),
    url(r'^iteration_stats/?$', iteration_stats_handler),
    url(r'^iteration_stats/(?P<iteration_id>[0-9]+)/?$', iteration_stats_handler),
    url(r'^saved_report/(?P<report_id>[0-9]+)/run?$', run_saved_report_handler),
    url(r'^saved_report/(?P<report_id>[0-9]+)/run/(?P<iteration_id>[0-9]+)?$', run_saved_report_handler),
    url(r'^saved_report/?$', saved_report_handler),
    url(r'^saved_report/(?P<report_id>[0-9]+)?$', saved_report_handler),
    url(r'^current/iterations/?$', current_iteration_handler),

    url(r'^iterations/?$', iteration_handler),
    url(r'^iterations/(?P<iteration_id>[0-9]+)/?$', iteration_handler),
    url(r'^iterations/(?P<iteration_id>[0-9]+)/burndown/?$', burndown_handler),
    url(r'^iterations/(?P<iteration_id>[0-9]+)/wiplimit/?$', wip_limit_handler),

    url(r'^sentiments/reportdata/?$', sentiment_report_handler),
    url(r'^iterations/(?P<iteration_id>[0-9]+)/sentiments/?$', iteration_sentiments_handler),
    url(r'^iterations/(?P<iteration_id>[0-9]+)/sentiments/(?P<sentiment_id>[0-9]+)/?$', iteration_sentiments_handler),
    url(r'^iterations/(?P<iteration_id>[0-9]+)/sentiments/team/(?P<team_slug>[-\w]+)/?$', iteration_sentiments_handler),

    url(r'^iterations/(?P<iteration_id>[0-9]+)/blockers/?$', story_blocker_handler), 

    url(r'^stories/?$', story_handler),
    url(r'^ministories/?$', mini_story_handler),
    url(r'^stories/(?P<story_id>[0-9]+)/convertepic?$', story_convert_epic_handler),
    url(r'^stories/(?P<story_id>[0-9]+)/duplicate?$', story_duplicate_handler),
    url(r'^stories/(?P<story_id>[0-9]+)/?$', story_handler),
    url(r'^stories/epic/(?P<epic_id>[0-9]+)/?$', story_handler),
    url(r'^stories/epic/(?P<epic_id>[+-]?[0-9]+)/?/(?P<archive>[0,1])$', story_handler),

    url(r'^stories/release/(?P<release_id>[0-9]+)/?$', story_handler),

    url(r'^stories/release/(?P<release_id>[-]?[0-9]+)/iteration/(?P<iteration_id>[0-9]+)/?$', story_handler),
    url(r'^stories/releaseteamstats/iteration/(?P<iteration_id>[0-9]+)/(?P<release_id>[0-9]+)/?$', release_teams_stats_handler),

    url(r'^stories/(?P<story_id>[0-9]+)/movetoproject/?$', move_story_handler),
    url(r'^stories/(?P<story_id>[0-9]+)/news/?$', story_newsfeed_handler),
    url(r'^iterations/[0-9]+/stories/(?P<story_id>[0-9]+)/news/?$', story_newsfeed_handler),
    url(r'^stories/(?P<story_id>[0-9]+)/reorder/?$', story_order_handler),

    url(r'^stories/assignmentoption/(?P<story_id>-?[0-9]+)/?$', assignment_options_handler),

    url(r'^iterations/(?P<iteration_id>[0-9]+)/stories/(?P<story_id>[0-9]+)/reorder/?$', story_order_handler),
    url(r'^iterations/(?P<iteration_id>[0-9]+)/stories/?$', story_handler),
    url(r'^iterations/(?P<iteration_id>[0-9]+)/epic/(?P<epic_id>[+-]?[0-9]+)/stories/?$', story_handler),
    url(r'^iterations/(?P<iteration_ids>[0-9,]+)/stories/?$', story_handler),
    url(r'^iterations/(?P<iteration_id>[0-9]+)/stories/(?P<story_id>[0-9]+)/attributes/?$', story_attr_handler),
    url(r'^iterations/(?P<iteration_id>[0-9]+)/stories/(?P<story_id>[0-9]+)/attributes/(?P<attr_id>[0-9]+)/?$',
        story_attr_handler),

    url(r'^attributes/?$', board_attr_handler),
    url(r'^attributes/(?P<attr_id>[0-9]+)/?$', board_attr_handler),
    url(r'^stories/?$', story_handler),
    url(r'^stories/(?P<story_id>[0-9]+)/agingdetails/?$', story_aging_handler),
    url(r'^stories/(?P<story_id>[0-9]+)/blockers/(?P<action>[a-z]+)/?$', story_blocker_handler),
    url(r'^stories/(?P<story_id>[0-9]+)/blockers/(?P<blocker_id>[0-9]+)/?$', story_blocker_handler),
    url(r'^stories/(?P<story_id>[0-9]+)/resetaging?$', story_aging_handler),
    url(r'^stories/links/?$', external_link_handler),
    url(r'^stories/(?P<story_id>[0-9]+)/links/?$', external_link_handler),
    url(r'^iterations/(?P<iteration_id>[0-9]+)/stories/(?P<story_id>[0-9]+)/?$', story_handler),
    url(r'^epics/?$', epic_handler),
    url(r'^epics/(?P<epic_id>[0-9]+)/?$', epic_handler),
    url(r'^epic/stats/?$', epic_stats_handler),
    url(r'^epic/stats/(?P<epic_id>[-]?[0-9]+)/?$', epic_stats_handler),
    url(r'^time_entries/?$', time_handler),
    url(r'^time_entries/(?P<entry_id>[0-9]+)/?$', time_handler),
    url(r'^time_entries/(?P<scope>[a-z]+)/?$', time_handler),
    url(r'^time_entries/story/(?P<story_id>[0-9]+)/?$', time_handler),
    url(r'^stories/(?P<story_id>[0-9]+)/tasks/?$', task_handler),
    url(r'^stories/(?P<story_id>[0-9]+)/tasks/(?P<task_id>[0-9]+)/?$', task_handler),
    url(r'^stories/(?P<story_id>[0-9]+)/tasks/(?P<task_id>[0-9]+)/reorder/?$', task_order_handler),
    url(r'^iterations/(?P<iteration_id>[0-9]+)/stories/(?P<story_id>[0-9]+)/tasks/?$', task_handler),
    url(r'^iterations/(?P<iteration_id>[0-9]+)/stories/(?P<story_id>[0-9]+)/tasks/(?P<task_id>[0-9]+)/?$',
        task_handler),
    url(r'^stories/(?P<story_id>[-]?[0-9]+)/attachments/?$', attachment_handler),
    url(r'^stories/(?P<story_id>[-]?[0-9]+)/attachments/(?P<attachment_id>[-]?[0-9]+)?$', attachment_handler),
    url(r'^stories/(?P<story_id>[-]?[0-9]+)/externalattachment$', attachment_handler),
    url(r'^stories/(?P<story_id>[-]?[0-9]+)/cover/attachments/(?P<attachment_id>[-]?[0-9]+){0,1}$', attachment_cover_handler),

    url(r'^workflows/?$', workflow_handler),
    url(r'^workflows/(?P<workflow_id>[0-9]+)/?$', workflow_handler),
    url(r'^workflows/(?P<workflow_id>[0-9]+)/steps/?$', workflow_steps_handler),
    url(r'^workflows/(?P<workflow_id>[0-9]+)/steps/(?P<workflow_step_id>[0-9]+)/?$', workflow_steps_handler),
    url(r'^workflows/(?P<workflow_id>[0-9]+)/steps/(?P<workflow_step_id>[0-9]+)/?/cells$',
        workflow_steps_handler,
        kwargs=dict(cells=True)),
    url(r'^boardcell/(?P<cell_id>[0-9]+)/?$', boardcell_handler),
    url(r'^boardcell/?$', boardcell_handler),
    url(r'^boardutil/(?P<action>[a-z]+)/?$', kanban_board_handler),
    url(r'^boardutil/(?P<action>[a-z]+)/(?P<template_type>[0-9]+)/?$', kanban_board_handler),
    url(r'^kstats/(?P<stat_type>[a-z]+)/?$', kanbanstats_handler),
    url(r'^kstats/(?P<stat_type>[a-z]+)/(?P<workflow_id>[\-0-9]+)/?$', kanbanstats_handler),
    url(r'^policy/(?P<policy_id>[0-9]+)/?$', policy_handler),
    url(r'^policy/?$', policy_handler),
    url(r'^graphic/(?P<graphic_id>[0-9]+)/?$', board_graphic_handler),
    url(r'^graphic/?$', board_graphic_handler),
    url(r'^header/(?P<header_id>[0-9]+)/?$', header_handler),
    url(r'^header/?$', header_handler),
    url(r'^image/(?P<image_id>[0-9]+)/?$', board_image_handler),
    url(r'^image/?$', board_image_handler),
    url(r'^point_scales/?$', point_scale_handler),
    url(r'^point_scales/(?P<scale_id>[0-9]+)/?$', point_scale_handler),
    url(r'^leadtime/?$', project_lead_time_handler),
    url(r'^notes/(?P<note_id>[0-9]+)/?$', project_notes_handler),
    url(r'^iteration/(?P<iteration_id>[0-9]+)/notes/?$', project_notes_handler),
    url(r'^iteration/(?P<iteration_id>[0-9]+)/notes/(?P<note_id>[0-9]+)/?$', project_notes_handler),
    url(r'^notes/(?P<note_id>[-]?[0-9]+)/attachments/?$', notes_attachment_handler),
    url(r'^notes/(?P<note_id>[-]?[0-9]+)/attachments/(?P<attachment_id>[-]?[0-9]+)?$', notes_attachment_handler),

    url(r'^teams/?$', team_handler),
    url(r'^team/?$', project_team_handler),

    url(r'^bigpicture/(?P<action>[a-z]+)/?$', pig_picture_stats_handler),
    url(r'^bigpicture/iteration/(?P<iteration_id>[0-9]+)/(?P<action>[a-z]+)/?$', pig_picture_stats_handler),
    url(r'^bigpicture/increment/(?P<increment_id>[0-9]+)/(?P<action>[a-z]+)/?$', pig_picture_stats_handler),
                       
    url(r'^systemrisks/?$', system_risks_handler),
    url(r'^systemrisks/iteration/(?P<iteration_id>[0-9]+)/?$', system_risks_handler),
    url(r'^dependencies/?$', project_dependencies_handler),

]

# All portfolio patterns get an organization_slug and a portfolio_id
portfolio_urlpatterns = [
    url(r'^risks/?$', risks_handler),
    url(r'^risks/targets/?$', risk_target_handler),
    url(r'^risks/(?P<risk_id>[0-9]+)/?$', risks_handler)
]


# All organization_urlpatterns get an organization_slug passed in
organization_urlpatterns = [
    url(r'^classic/projects$', classic_project_handler),
    url(r'^users$', all_users_handler),
    url(r'^teams$', team_handler),
    url(r'^teams/(?P<team_id>[0-9]+)/?$', team_handler),
    url(r'^teams/(?P<team_id>[0-9]+)/(?P<action>[a-zA-Z]+)$', team_handler),
    url(r'^my_stories$', current_stories_handler),
    url(r'^active_stories$', my_stories_handler),
    url(r'^me', user_handler),
    url(r'^releases/(?P<release_id>[0-9]+)/?$', release_handler),
    url(r'^subscription/code/?$', subscription_code_handler),
    url(r'^subscription/?$', subscription_handler),
    url(r'^extras/github/?$', github_handler),
    url(r'^releases/(?P<release_id>[0-9]+)/ministories/(?P<portfolio_root_slug>[-\w]+)/?$', mini_story_handler),
    url(r'^releases/(?P<release_id>[0-9]+)/stories/(?P<project_slug>[-\w]+)/?$', release_stories_handler),
    url(r'^releases/(?P<project_slug>[-\w]+)/?$', project_release_handler),
    url(r'^releases/(?P<release_id>[-]?[0-9]+)/stories/(?P<project_slug>[-\w]+)/stats/(?P<load_child>[0,1])/?$',
        release_stories_stats_handler),


    url(r'^projects/?$', project_handler),
    url(r'^dashprojects/?$', dashboard_projects_handler),
    url(r'^projects/(?P<project_slug>[-\w]+)/?$', project_handler),
    url(r'^projects/(?P<project_slug>[-\w]+)/', include(project_urlpatterns)),

    url(r'^newsfeed/grouped/(?P<start_day>[0-9]+)/(?P<end_day>[0-9]+)/?$', grouped_newsfeed_handler),
    url(r'^portfolio/build?$', portfolio_build_handler),
    url(r'^portfolio/?$', portfolio_handler),
    url(r'^portfolio/project/(?P<project_slug>[-\w]+)/?$', portfolio_handler),

    url(r'^portfolio/(?P<portfolio_id>[0-9]+)/?$', portfolio_handler),
    url(r'^portfolio/(?P<portfolio_id>[0-9]+)/', include(portfolio_urlpatterns)),

    url(r'^search/?$', search_handler),
    url(r'^time_entries/?$', time_handler),
    url(r'^time_entries/(?P<scope>[a-z]+)/?$', time_handler),
    url(r'^time_entries/(?P<entry_id>[0-9]+)?$', time_handler),
    url(r'^releasestats/?$', release_stat_handler),
    url(r'^releasestats/(?P<release_id>[0-9]+)/(?P<scope>[a-z]*)/?$', release_stat_handler),
    url(r'^releasestats/project/(?P<project_slug>[-\w]+)/(?P<scope>[a-z]*)/?$', release_stat_handler),
    url(r'^releasestats/project/(?P<project_slug>[-\w]+)/iteration/(?P<iteration_id>[0-9]+)/childstats/?$', release_child_stat_handler),
    url(r'^releasestats/project/(?P<project_slug>[-\w]+)/iteration/(?P<iteration_id>[0-9]+)/(?P<scope>[a-z]*)/?$', release_stat_handler),
    url(r'^increment/(?P<increment_id>[0-9]+)/dependencies/?$', program_increment_dependency_handler),
    url(r'^timeline/project/(?P<project_slug>[-\w]+)/?$', timeline_story_handler),
    url(r'^timeline/project/(?P<project_slug>[-\w]+)/(?P<iteration_id>[0-9]+)/?$', timeline_story_handler)


]

urlpatterns = (
    url(r'^query/?$', query_handler),
    url(r'^query/(?P<query_id>[0-9]+)/?$', query_handler),
    url(r'^calendar$', calendar_view_handler),

    url(r'^job/(?P<job_id>[0-9]+)$', job_handler),
    url(r'^offlinejob/(?P<job_id>[0-9]+)$', offline_job_handler),
    url(r'^organizations/$', org_handler),

    url(r'^favorite/project/(?P<project_slug>[-\w]+)$', favorites_handler),

    url(r'^account/token$', account_token_handler),
    url(r'^account/me$', account_settings_handler),
    url(r'^account/email$', email_confirmation_handler),
    url(r'^account/email_subscriptions$', email_subscription_handler),
    url(r'^account/(?P<email_id>[0-9]+)/email$', email_confirmation_handler),
    url(r'^account/(?P<action>[a-zA-Z]+)/email$', email_confirmation_handler),
    url(r'^account/getpassword$', change_password_handler),
    url(r'^account/avatar$', upload_avatar_handler),
    url(r'^account/(?P<action>[a-zA-Z]+)/avatar$', upload_avatar_handler),
    url(r'^account/deleteaccount$', delete_account_handler),
    url(r'^account/OAuthApp$', oauth_app_handler),
    url(r'^account/addOAuthApp$', oauth_app_handler),
    url(r'^account/OAuthToken$', oauth_token_handler),
    url(r'^account/revokeOAuthToken$', oauth_token_handler),
    url(r'^account/OpenID$', openid_app_handler),
    url(r'^account/github$', github_user_handler),
    url(r'^shared/(?P<share_key>[0-9a-z]+)$', shared_project_handler),
    url(r'^shared/(?P<share_key>[0-9a-z]+)/story/(?P<story_id>[0-9]+)', shared_story_handler),

    url(r'^organizations/subscription/?$', subscription_plan_handler),

    url(r'^organizations/(?P<organization_slug>[-\w]+)/?$', org_handler),
    url(r'^organizations/(?P<organization_slug>[-\w]+)/', include(organization_urlpatterns)),

                       
    url(r'^comments/story/(?P<story_id>[0-9]+)/?$', story_comments_handler),
    url(r'^comments/story/(?P<story_id>[0-9]+)/?/comment/(?P<comment_id>[0-9]+)/?$', story_comments_handler),
    url(r'^comments/notes/(?P<note_id>[0-9]+)/?$', notes_comments_handler),
    url(r'^comments/notes/(?P<note_id>[0-9]+)/?/comment/(?P<comment_id>[0-9]+)/?$', notes_comments_handler),
    url(r'^dependencies/story/(?P<story_id>[0-9]+)/dependency/(?P<dependent_story_id>[0-9]+)/?$',
        story_dependencies_handler),
    url(r'^dependencies/story/(?P<story_id>[0-9]+)/dependency/?$', story_dependencies_handler),

    url(r'^docs$', views.docs, name="docs"),
    url(r'^resources/resources.json$', views.resources, name="resources_json"),
    url(r'^resources/(?P<resource_name>[-\w]+)$', views.resources, name="resource_discovery"),
    url(r'^oauth/apps$', views.oauth_apps, name="oauth_apps"),
    url(r'^oauth/access$', views.oauth_access, name="oauth_access"),

    url(r'^oauth/request_token/$', authentication.oauth_request_token),
    url(r'^oauth/authorize/$', authentication.oauth_user_auth),
    url(r'^oauth/access_token/$', authentication.oauth_access_token),
)
