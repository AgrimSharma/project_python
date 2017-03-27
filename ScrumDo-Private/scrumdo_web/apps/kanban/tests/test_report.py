import apps.kanban.stats as kstat
import apps.kanban.managers as kanban_manager

from django.contrib.auth.models import User
from apps.kanban.models import RebuildMovementJob
from apps.tests.mixins import BaseMixinTest, StaffMixinTest


class ReportTest(StaffMixinTest):
    """
    Project report unit tests
    """
    def setUp(self):
        super(ReportTest, self).setUp()
        self.init_project(name='Sample Project')
        self.other_user = User.objects.get(id=5) # user 'read'
        self.story = self.project.stories.all()[0]
        self.story.assignee.add(self.other_user)

        #request.GET parameters
        self.workflow = kanban_manager.getDefaultWorkflow(self.project)
        self.show_backlog = False
        self.assignee_id = [self.other_user.id]
        self.tag = None
        self.epic = None
        self.detail = False
        self.yaxis  = 1
        self.iteration = 'All'
        self.startdate = self.enddate = None


    def test_report_cfd(self):
        """
        Unit test for project report cfd
        """
        graph = kstat.calculateCFD(
            self.project, self.workflow, self.show_backlog, self.assignee_id,
            self.tag, self.epic, self.detail, self.yaxis, self.iteration, self.startdate, self.enddate)

        RebuildMovementJob.objects.filter(project=self.project).delete()
        response = self.client.get("/api/v3/organizations/test-organization/projects/%s/kstats/cfd/%s/" % (self.project.slug, self.workflow.id), {
                'cfd_show_backlog': self.show_backlog,
                'assignee_id': self.assignee_id,
                'tag': self.tag,
                'epic': self.epic,
                'detail': self.detail,
                'yaxis': self.yaxis,
                'iteration': self.iteration,
                'startdate': self.startdate,
                'enddate': self.enddate
            })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), graph)
