from django.test import TestCase
from django.conf import settings

from apps.projects.tasks import record_all_burnup_charts
from apps.kanban.tasks import record_all_project_stats
from apps.projects.tasks import update_mixpanel
from apps.projects.tasks import site_stats
from apps.kanban.tasks import check_cell_movements
from apps.email_notifications.tasks import send_daily_digest
from apps.email_notifications.tasks import send_iteration_reports
from apps.email_notifications.tasks import send_notifications
from apps.email_notifications.tasks import send_queued_mail
from apps.email_notifications.tasks import retry_deferred
from apps.extras.tasks import process_queue
from apps.extras.tasks import setup_pull_queue
from apps.projects.tasks import update_solr_1_hour
from apps.activities.tasks import purge_old


class JobsTest(TestCase):
    """A simple test that just tries to run all our scheduled jobs to make sure none of them
       throw an exception."""
    fixtures = ["sample_organization.json"]

    def setUp(self):
        settings.ROLLBAR['access_token'] = ''
        settings.ROLLBAR['environment'] = ''

    def test_jobs(self):
        record_all_burnup_charts()
        record_all_project_stats()
        update_mixpanel()
        site_stats()
        check_cell_movements()
        send_daily_digest()
        send_iteration_reports()
        send_notifications()
        send_queued_mail()
        retry_deferred()
        process_queue()
        setup_pull_queue()
        update_solr_1_hour()
        purge_old()