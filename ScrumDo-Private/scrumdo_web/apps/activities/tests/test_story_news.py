# sample_organization provides the following:
#
# organization: test-organization
# projects: test-project training29957
# users: staff read write
#
# org/projects are set up as in their intitial states except for the creation of some additional teams.

from django.test import TestCase
from django.conf import settings

import apps.projects.models as project_models
import apps.activities.models as activity_models
import apps.projects.signals as signals


import logging

logger = logging.getLogger(__name__)


class StoryNewsTest(TestCase):
    fixtures = ["sample_organization.json"]

    def setUp(self):
        settings.ROLLBAR['access_token'] = ''
        settings.ROLLBAR['environment'] = ''

    def test_story_news(self):
        request = None

        project = project_models.Project.objects.get(slug='test-project')
        old_news_count = activity_models.NewsItem.objects.filter(related_story__project=project).count()

        user = project.creator

        story = project_models.Story(project=project, summary="Hi There!",
                                     local_id=project.getNextId(), creator=user, iteration_id=1)
        story.save()
        signals.story_created.send(sender=request, story=story, user=user)

        self.assertEqual(activity_models.NewsItem.objects.filter(related_story__project=project).count(),
                         old_news_count + 1)

        news = activity_models.NewsItem.objects.filter(related_story__project=project).order_by("-created")[0]
        self.assertEqual(news.related_story, story)
        self.assertEqual(news.text, u'\ncreated card <a href="/projects/story_permalink/17">PP-1</a> in <a href="/projects/test-project/iteration/1">Test Project / Backlog</a>. <i><p>Hi There!</p></i>\n\n\n\n')

        story.summary = "TEST SUMMARY"
        story.save()
        diffs = {'summary': ('old', 'new')}
        signals.story_updated.send(sender=request, story=story, diffs=diffs, user=user)

        self.assertEqual(activity_models.NewsItem.objects.filter(related_story__project=project).count(),
                         old_news_count + 2)
