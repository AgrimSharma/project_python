
from .common import *
from decimal import *
from django.utils.html import strip_tags

from django.conf import settings

# from apps.projects.models import Iteration
from apps.projects.models import *
from apps.projects.models.story import ProjectAssignments
from apps.attachments.models import Attachment, Tmpattachment
from apps.projects.calculation import onDemandCalculateVelocity, calculateEpicStats
from apps.projects.access import *
from apps.projects import search_views
from apps.projects.managers import broadcastIterationCounts, reorderStory, setRelativeRank, \
transferLabels, transferTags, transferBlockers, transferRelease

import apps.projects.signals as signals
from apps.projects.util import extractInlineImagesForStory
import apps.projects.tasks as projects_tasks

from apps.realtime import util as realtime_util

from apps.kanban.models import BoardCell, CellMovement, Iteration
import apps.kanban.managers as kanban_manager

import apps.activities.utils as utils
import apps.organizations.tz as tz

from haystack import connections

from django.db.models import Max, Q
from django.core.exceptions import ObjectDoesNotExist

import datetime


def _moveStoryOutOfCell(story, project, user):
    if story.cell is None:
        return  # Already not in a cell, no worries.
    logger.debug ('Story Iteration_TYPE: %s' %story.iteration.iteration_type)
    if story.iteration.iteration_type != Iteration.ITERATION_WORK:
        # Here,
        #  1. The story is not in a "work" iteration (backlog or archive)
        #  2. The project is a kanban project
        #  3. The story is in a cell
        # Therefore, the cell assignment is bogus
        kanban_manager.moveStoryOntoCell(story, None, user)


def _moveStoryOntoCell(data, story, project, user):
    if "cell_id" in data and story.cell_id != data["cell_id"]:
        cell_id = data["cell_id"]
        logger.debug("Moving the cell the story is in.")
        try:
            if story.id is None:
                story.save()
            cell = project.boardCells.get(id=cell_id)
            
            kanban_manager.moveStoryOntoCell(story, cell, user)

            story.cell_id = data["cell_id"]
        except BoardCell.DoesNotExist:
            logger.warn("Tried to move story out of a cell that does not exist.")


class StoryAssignmentHandler(BaseHandler):
    allowed_methods = ('GET', 'POST', 'DELETE')

    @staticmethod
    def assignments(parent_iteration, project):
        stories = parent_iteration.stories.filter(project_assignments=project)
        return [s.id for s in stories]

    @staticmethod
    def get_parent(increment_id, user):
        increment = ProgramIncrement.objects.get(id=increment_id)
        parent_iteration = increment.iteration
        parent_project = parent_iteration.project
        read_access_or_403(parent_project, user)
        return parent_iteration, parent_project

    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, increment_id, project_slug):
        org, project = checkOrgProject(request, organization_slug, project_slug)
        parent_iteration, parent_project = self.get_parent(increment_id, request.user)
        card_view = request.GET.get("cards", "false") == "true"
        if card_view is False:
            return self.assignments(parent_iteration, project)
        else:
            return parent_iteration.stories.filter(project_assignments=project)

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def create(self, request, organization_slug, increment_id, project_slug, story_id):
        org, project = checkOrgProject(request, organization_slug, project_slug, True)
        parent_iteration, parent_project = self.get_parent(increment_id, request.user)
        story = parent_iteration.stories.get(id=story_id)
        project_assignments = ProjectAssignments(story = story, project = project)
        project_assignments.save()
        return self.assignments(parent_iteration, project)

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def delete(self, request, organization_slug, increment_id, project_slug, story_id):
        org, project = checkOrgProject(request, organization_slug, project_slug, True)
        parent_iteration, parent_project = self.get_parent(increment_id, request.user)
        story = parent_iteration.stories.get(id=story_id)
        ProjectAssignments.objects.filter(story = story, project = project).delete()
        return self.assignments(parent_iteration, project)


class StoryWithIterationHandler(BaseHandler):
    """This is used with the apiMapper hack to make search results include an iteration for stories."""
    allowed_methods = ()
    fields = ("id",
                "number",
                "completed_task_count",
                "rank",
                "category",
                "business_value",
                "detail",
                "comment_count",
                "has_attachment",
                ("epic",("local_id","id")),
                "epic_label",
                "task_count",
                "created",
                "modified",
                "iteration_id",
                "summary",
                "points",
                "extra_1",
                "extra_2",
                "extra_3",
                "points_value",
                "tags",
                "tags_list",
                "task_counts",
                "cell_id",
                "has_external_links",
                "assignee",
                # "dependency",
                "commits",
                "cell",
                ("labels", ("id", "name", "color")),
                ("creator", ("username", "first_name", "last_name")),
                "reorderResults",
                "iteration",
                "project_slug",
                'release',
                'age_hours',
                "blocked",
                "time_criticality",
                "time_criticality_label",
                "risk_reduction",
                "risk_reduction_label",
                "wsjf_value",
                "business_value_label",
                'age_hours',
                "prefix",
                'feature_stats',
                "global_backlog_card")

    @staticmethod
    def global_backlog_card(story):
        if story.project.project_type == Project.PROJECT_TYPE_BACKLOG_ONLY:
            return {"type": story.project.work_item_name}
        else:
            return None

    @staticmethod
    def release(story):
        if story.release_id is None:
            return None
        return {
            'id': story.release.id,
            'number': story.release.local_id,
            'iteration_id': story.release.iteration_id,
            'project_slug': story.release.project.slug,
            'project_prefix': story.release.project.prefix,
            'summary': story.release.summary
        }


    @staticmethod
    def cell(story):
        cell = story.cell
        if cell is None:
            return None
        return {'id': cell.id, 'label': cell.label, 'full_label': cell.full_label, 'color': cell.headerColor, 'type': cell.time_type}

    @staticmethod
    def project_slug(story):
        return story.project.slug

    @staticmethod
    def commits(story):
        if not story.has_commits:
            return []
        return story.commits.all()

    @staticmethod
    def assignee(story):
        # ("assignee",("id","username","first_name","last_name")),
        if story.assignees_cache == "":
            return []
        r = []
        for assignee in story.assignee.all():
            r.append({
                    "id": assignee.id,
                    "username": assignee.username,
                    "first_name": assignee.first_name,
                    "last_name": assignee.last_name
                })
        return r


    @staticmethod
    def reorderResults(story):
        try:
            return story.reorderResults
        except:
            return None

    @staticmethod
    def task_counts(story):
        return story.taskCountsArray()

    @staticmethod
    def tags_list(story):
        return story.story_tags_array()

    @staticmethod
    def number(story):
        return story.local_id

    @staticmethod
    def points(story):
        return story.getPointsLabel()

    @staticmethod
    def points_value(story):
        return story.points_value()

    @staticmethod
    def risk_reduction(story):
        return story.risk_reduction_value()

    @staticmethod
    def time_criticality(story):
        return story.time_criticality_value()

    @staticmethod
    def risk_reduction_label(story):
        return story.getRiskReductionLabel()

    @staticmethod
    def time_criticality_label(story):
        return story.getTimeCriticalityLabel()

    @staticmethod
    def wsjf_value(story):
        return story.wsjfValue();

    @staticmethod
    def business_value(story):
        return story.businessValue()

    @staticmethod
    def business_value_label(story):
        return story.getBusinessValueLablel()


    # lets return project prefix to org wide search
    # we don't have access to project there
    @staticmethod
    def prefix(story):
        return story.project.prefix
        

storyWithIterationHandler = StoryWithIterationHandler()


class StoryHandler(BaseHandler):
    allowed_methods = ('GET', 'PUT', 'POST', "DELETE")
    write_fields = ("estimated_minutes", "category", "business_value", 'epic_rank', 'release_rank', 'due_date')
    html_write_fields = ("summary", "detail", "extra_1", "extra_2", "extra_3")
    model = Story
    ALLOW_STREAM = True
    fields = ("id",
                "number",
                "completed_task_count",
                "rank",
                "epic_rank",
                'release_rank',
                "detail",
                "comment_count",
                "has_attachment",
                "epic",
                "epic_label",
                "task_count",
                "created",
                "modified",
                "iteration_id",
                "iteration_name",
                "iteration_end_date",
                "summary",
                "business_value",
                "points",
                "extra_1",
                "extra_2",
                "extra_3",
                "points_value",
                "tags",
                "tags_list",
                "task_counts",
                "cell_id",
                "has_external_links",
                "assignee",
                # "dependency",
                "commits",
                "pull_requests",
                "cell",
                "labels",
                ("creator", ("username", "first_name", "last_name")),
                "reorderResults",
                "estimated_minutes",
                "project_slug",
                'due_date',
                'release',
                'age_hours',
                'blocked',
                "time_criticality",
                "time_criticality_label",
                "risk_reduction",
                "risk_reduction_label",
                "wsjf_value",
                "business_value_label",
                'age_hours',
                'cover_image',
                'feature_stats',
                'prefix',
                'global_backlog_card')
    
    @staticmethod
    def global_backlog_card(story):
        if story.project.project_type == Project.PROJECT_TYPE_BACKLOG_ONLY:
            return {"type": story.project.work_item_name}
        else:
            return None

    @staticmethod
    def cover_image(story):
        attachment = story.attachments.all().filter(cover_image=True).first()
        if attachment is not None:
            return {"url": attachment.attachment_file.url,
                    "id": attachment.id}
        else:
            return None

    @staticmethod
    def iteration_name(story):
        return story.iteration.name

    @staticmethod
    def iteration_end_date(story):
        return story.iteration.end_date

    @staticmethod
    def release(story):
        if story.release_id is None:
            return None
        return {
            'id': story.release.id,
            'number': story.release.local_id,
            'iteration_id': story.release.iteration_id,
            'project_slug': story.release.project.slug,
            'project_prefix': story.release.project.prefix,
            'summary': story.release.summary
        }

    @staticmethod
    def labels(story):
        return story.labels.all()

    @staticmethod
    def cell(story):
        cell = story.cell
        if cell is None:
            return None
        return {'id': cell.id, 'label': cell.label, 'full_label': cell.full_label, 'color': cell.headerColor, 'type': cell.time_type}

    @staticmethod
    def epic(story):
        if story.epic:
            return {
                "local_id": story.epic.local_id,
                "id": story.epic.id
            }
        else:
            return None

    @staticmethod
    def project_slug(story):
        if hasattr(story, "project_slug"):
            return story.project_slug  # in the newsfeed handler, we set this to avoid a project lookup
        else:
            return story.project.slug

    @staticmethod
    def pull_requests(story):
        if not story.has_commits:
            return []
        return story.pull_requests.all()

    @staticmethod
    def commits(story):
        if not story.has_commits:
            return []
        return story.commits.all()

    @staticmethod
    def assignee(story):
        if story.assignees_cache == "":
            return []
        r = []
        for assignee in story.assignee.all():
            r.append({
                    "id": assignee.id,
                    "username": assignee.username,
                    "first_name": assignee.first_name,
                    "last_name": assignee.last_name
                })
        return r


    @staticmethod
    def reorderResults(story):
        try:
            return story.reorderResults
        except:
            return None

    @staticmethod
    def task_counts(story):
        return story.taskCountsArray()

    @staticmethod
    def tags_list(story):
        return story.story_tags_array()

    @staticmethod
    def number(story):
        return story.local_id

    @staticmethod
    def points(story):
        return story.getPointsLabel()

    @staticmethod
    def points_value(story):
        return story.points_value()

    @staticmethod
    def risk_reduction(story):
        return story.risk_reduction_value()

    @staticmethod
    def time_criticality(story):
        return story.time_criticality_value()

    @staticmethod
    def risk_reduction_label(story):
        return story.getRiskReductionLabel()

    @staticmethod
    def time_criticality_label(story):
        return story.getTimeCriticalityLabel()

    @staticmethod
    def wsjf_value(story):
        return story.wsjfValue();

    @staticmethod
    def business_value(story):
        return story.businessValue()

    @staticmethod
    def business_value_label(story):
        return story.getBusinessValueLablel()

    # lets return project prefix to show stories for a feature
    @staticmethod
    def prefix(story):
        return story.project.prefix

    @staticmethod
    def feature_stats(story):
        # will return number of stories having this as a release and number of project's child (teams)
        project = story.project
        org = project.organization
        story_count = Story.objects.filter(project__organization=org, release=story).count()
        teams = story.project_assignments.all().count()
        return {"story_count": story_count, "teams": teams}


    @staticmethod
    def _reorderStory(story, data, project):
        # PLEASE REMEMBER - both this and the story order handler can reorder stories, so modify both if you modify one.
        modified = []
        before_id = data["story_id_before"]
        after_id = data["story_id_after"]
        modifiedOtherStories, modified = reorderStory(story, before_id, after_id, story.iteration)
        story.save()
        return {'modifiedOther': modifiedOtherStories, 'newRank': story.rank, 'storiesModified': modified}

    @staticmethod
    def _updateStory(story, data, project, request):
        if "epic_id" in data:  # TODO: Deprecate and remove epic_id from here.
            if data['epic_id'] is not None:
                epic = Epic.objects.get(id=data['epic_id'])
                if epic.project != project:
                    raise PermissionDenied("You don't have access to that epic")
                story.epic = epic
            else:
                story.epic = None
        elif "epic" in data:
            if data['epic'] is not None and 'id' in data['epic'] and data['epic']['id'] not in ['', None]:
                epic = Epic.objects.get(id=data['epic']['id'])
                if epic.project != project:
                    raise PermissionDenied("You don't have access to that epic")
                story.epic = epic
            else:
                story.epic = None

        if "release" in data:
            if data["release"] is None:
                story.release_id = None
            else:
                story.release_id = data["release"].get("id", None)

        for field in StoryHandler.html_write_fields:
            if field in data:
                #setattr(story, field, linkStories(data[field], project))
                setattr(story, field, linkStoriesVer2(data[field], project))

        for field in StoryHandler.write_fields:
            if field in data:
                setattr(story, field, data[field])

        if "force_rank" in data:
            story.rank = data['force_rank']

        if story.rank is None:
            # Somehow, this is occasionally happening, I'm stumped!
            story.rank = 500000

        if "points" in data:
            p = data["points"]
            scale = project.getPointScale()
            for entry in scale:
                if (entry[1] == p) or (entry[0] == p):
                    story.points = entry[0]
                    break

        if "risk_reduction_label" in data:
            p = data["risk_reduction_label"]
            scale = project.getPointScale()
            for entry in scale:
                if (entry[1] == p) or (entry[0] == p):
                    story.risk_reduction = entry[0]
                    break

        if "time_criticality_label" in data:
            p = data["time_criticality_label"]
            scale = project.getPointScale()
            for entry in scale:
                if (entry[1] == p) or (entry[0] == p):
                    story.time_criticality = entry[0]
                    break

        if "business_value" in data:
            bv = data["business_value"]
            # handle unexpected values
            try:
                if project.business_value_mode != Project.BUSINESS_VALUE_AS_DOLLAR:
                    scale = project.getPointScale()
                    valueFound = False
                    for entry in scale:
                        if (entry[1] == bv) or (entry[0] == bv):
                            story.business_value = Decimal(str(entry[0]))
                            valueFound = True
                            break
                    if not valueFound:
                        if(bv==None):
                            story.business_value=None
                        else:
                            story.business_value = Decimal(str(bv))
                else:
                    story.business_value = Decimal(str(bv))
            except:
                story.business_value = None

        _moveStoryOntoCell(data, story, project, request.user)
        story.full_clean()

        if "tags" in data:
            story.tags = data["tags"]

        if "assignee" in data:
            data['assignees'] = ",".join( [a["username"] for a in data['assignee']] )

        if "assignees" in data:
            if story.id is None:
                story.save()  # need to save before setting assignees for new stories.
            logger.debug("Setting assingees to %s" % data["assignees"])
            story.assignees = data["assignees"]

        if "labels" in data:
            labels = data["labels"]
            story.labels.clear()
            for label in labels:
                try:
                    l = project.labels.get(id=label['id'])
                    story.labels.add(l)
                except:
                    pass
            # logger.info(story.labels.all())

        story.full_clean()
        story.resetCounts()

        if "extra_attributes" in data:
            for data in data['extra_attributes']:
                logger.debug("Setting %s" % data)
                try:
                    attr = StoryAttributes.objects.get(story=story, context=data['context'], key=data['key'])
                    attr.value = data['value']
                    attr.save()
                except StoryAttributes.DoesNotExist:
                    attr = StoryAttributes(story=story, context=data['context'], key=data['key'], value=data['value'])
                    attr.save()

        if extractInlineImagesForStory(story):
            story.save()
        onDemandCalculateVelocity(project)
        kanban_manager.moveStoryOntoDefaultCell(story, project, request.user)
        # realtime_util.send_story_modified(project, story)
        # rebuild Story Related System Risks Cache
        projects_tasks.rebuildStoryRisks.apply_async((project, story.iteration_id), countdown=10)
        return story

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def delete(self, request, organization_slug, project_slug, story_id, iteration_id=None):
        data = request.data
        org, project = checkOrgProject(request, organization_slug, project_slug, True)

        story = Story.objects.get(id=story_id)
        if story.project != project:
            raise ValidationError("Organization and project don't match")

        signals.story_deleted.send(sender=request, story=story, user=request.user)
        epic = story.epic
        release = story.release
        story.sync_queue.clear() # clears the queue on the story
        iteration_id = story.iteration_id
        
        kanban_manager._remove_story_history(story) # delete backloghistorystory object

        if story.iteration.iteration_type == Iteration.ITERATION_TRASH:
            story.delete()
            if epic is not None:
                calculateEpicStats(epic)

            if release is not None:
                projects_tasks.QueueMacroStatusCalc(None, release.id)

        else:
            self._deleteSingleStory(request, story_id, data, project)



        onDemandCalculateVelocity(project)
        realtime_util.send_story_delete(project, story_id)
        # rebuild Story Related System Risks Cache
        projects_tasks.rebuildStoryRisks.apply_async((project, story.iteration_id), countdown=10)

        return "deleted"


    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def update(self, request, organization_slug, project_slug, story_id=None, iteration_id=None, mode=None):
        data = request.data
        org, project = checkOrgProject(request, organization_slug, project_slug, True)
        try:
            realtime_util.lock_realtime_project(project)
            if story_id is not None:
                # Updating a single story
                result = self._updateSingleStory(request, story_id, iteration_id, data, project)
                projects_tasks.queueUpdateSolr(story_id)
                return result

            # Otherwise, this is a batch-update
            result = []
            logger.info("Bulk Update, %d entries" % len(data))
            for entry in data:
                story_id = entry["id"]
                result.append(self._updateSingleStory(request, story_id, iteration_id, entry, project))

            for entry in data:
                # Update indexes after all stories are saved.
                story_id = entry["id"]
                projects_tasks.queueUpdateSolr(story_id)

            return result
        finally:
            realtime_util.unlock_realtime_project(project)

    def _checkForComment(self, story, data, request):
        if "newComment" in data and len(data['newComment']) > 1:
            comment = StoryComment(story=story,
                                   user=request.user,
                                   comment=data["newComment"])
            comment.save()
            story.resetCommentCount()
            story.save()

    def _checkForTempAttachments(self, story, project, request):
        tmpAttachments = Tmpattachment.objects.filter(sessionkey=request.session.session_key,
                                                      creator=request.user, project=project)
        for tmpAttachment in tmpAttachments:
            attchment = Attachment(creator = request.user)
            attchment.story = story
            attchment.attachment_file = tmpAttachment.attachment_file
            attchment.attachment_url = tmpAttachment.attachment_url
            attchment.attachment_name = tmpAttachment.attachment_name
            attchment.thumb_url = tmpAttachment.thumb_url
            attchment.attachment_type = tmpAttachment.attachment_type
            attchment.save()
            tmpAttachment.delete()

    
    def _checkForDependencies(self, story, data, request):
        if "dependencies" in data and len(data["dependencies"]) > 0:
            dependencies = data["dependencies"]
            for dependency in dependencies:
                dependencyId = dependency['id']
                if dependencyId == story.id:
                    continue
                
                dependentStory = Story.objects.get(id=dependencyId)
                if has_read_access(dependentStory.project, request.user): 
                    story.dependency.add(dependentStory)

    def _checkForRisks(self, story, data, request):
        if "risks" in data and len(data["risks"]) > 0:
            risks = data["risks"]
            project = story.project
            write_fields = ("description","probability","severity_1","severity_2",\
                            "severity_3","severity_4","severity_5","severity_6","severity_7")
            try:
                portfolio = project.portfolio_level.portfolio
                for risk in risks:
                    R = Risk(portfolio=portfolio)

                    for fieldname in write_fields:
                        value = risk.get(fieldname, None)
                        if value is not None:
                            setattr(R, fieldname, value)
                    R.save()
                    R.cards.add(story)
            except Exception, e:
                logger.error('Failed to add risk to story: '+ str(e))

    def _updateSingleStory(self, request, story_id, iteration_id, data, project):
        iteration = None

        story = Story.objects.get(id=story_id)
        story.skip_haystack = True  # WARNING - MAKE SURE YOU MANUALLY UPDATE INDEX AT THE END.

        if story.project != project:
            raise ValidationError("Organization and project don't match")

        # Save a copy so we can get diffs at the end.
        old_story = story.__dict__.copy()

        #Save a copy of labels from old story
        lable_dict = {}
        for label in story.labels.all():
            lable_dict[label.id] = {'name': label.name, 'color': label.color}

        # The order here is important.
        # First, we need to set the new iteration.  This is required because _updateStory
        # uses that new iteration in the call to move into a cell.
        iterationChanged = False
        if iteration_id:
            iteration = project.iterations.get(id=iteration_id)
            if iteration.project != project:
                raise ValidationError("Organization and project don't match")
            iterationChanged = story.iteration != iteration
            story.iteration = iteration

        # Then we can update all the other fields via _updateStory
        # This includes moving it into a cell if appropriate.
        result = self._updateStory(story, data, project, request)  # Need to do this BEFORE _moveStoryOutOfCell below

        if iterationChanged:
            broadcastIterationCounts(project)
            if iteration.iteration_type == Iteration.ITERATION_WORK:
                # We changed iteration, and the new iteration is a work iteration.
                # so if we have a cell set, we want to record that movement.
                # also, if we don't have a cell, we should record a movement to the null cell (so no more "if" here)
                
                kanban_manager.moveStoryOntoCell(story, story.cell, request.user)

            else:
                # If we moved into backlog or archive, they don't have cells.
                # We want to update the cell-movements
                # so it shows it was removed from the cell on reports.
                logger.debug("Moving story to archive.")
                _moveStoryOutOfCell(story, project, request.user)

        # There's a special story_id_before/story_id_after pair that can be set to affect reordering
        # of the story.  We do this last so the _reorderStory algorithm can make inferences from
        # the current story data.
        if ("story_id_before" in data) and ("story_id_after" in data):
            result.reorderResults = self._reorderStory(story, data, project)

        story.save()

        self._checkForComment(story, data, request)

        # lables from new stroy
        new_lable_dict = {}
        for label in story.labels.all():
            new_lable_dict[label.id] = {'name': label.name, 'color': label.color}

        # add labels to the both dict
        old_story_copy = old_story.copy()
        story_copy = story.__dict__.copy()
        old_story_copy['labels'] = lable_dict
        story_copy['labels'] = new_lable_dict

        diffs = utils.model_differences(old_story_copy, story_copy, ["modified"], dicts=True)
        signals.story_updated.send(sender=request, story=story, diffs=diffs, user=request.user)

        if 'release_id' in diffs:
            projects_tasks.queueMacroStatsCalc(story.id, diffs['release_id'][0])

        if 'epic_id' in diffs:
            oldEpicId = diffs['epic_id'][0]
            if oldEpicId is not None:
                oldEpic = Epic.objects.get(id=oldEpicId)
                calculateEpicStats(oldEpic)

        # These are the fields that could cause stats for a release or epic to change.
        fields = ('cell_id', 'points', 'iteration_id', 'project_id', 'epic_id', 'release_id')

        if story.release is not None:
            if any(f in diffs for f in fields):
                projects_tasks.queueMacroStatsCalc(story.id, None)

        if story.epic is not None:
            # If any of the following fields have changed and we have an epic set, we need
            # to recalculate the epic stats.
            if any(f in diffs for f in fields):
                calculateEpicStats(story.epic)

        props = {k: v[1] for k, v in diffs.iteritems()}

        extraPatchFields = {
            'cell': self.cell,
            'assignee': self.assignee,
            'tags_list': self.tags_list,
            'points_value': self.points_value,
            'labels': lambda obj: [{"id": label.id, "name": label.name, "color": label.color} for label in obj.labels.all()]
        }

        for k, v in extraPatchFields.iteritems():
            props[k] = v(story)

        realtime_util.send_story_patch(project, story, props)
        return result

    def _deleteSingleStory(self, request, story_id, data, project):
        iteration = None
        story = Story.objects.get(id=story_id)

        if story.project != project:
            raise ValidationError("Organization and project don't match")

        # The order here is important.
        # First, we need to set the new iteration.  This is required because _updateStory
        # uses that new iteration in the call to move into a cell.
        iterationChanged = False
        try:
            iteration = Iteration.objects.get(iteration_type=Iteration.ITERATION_TRASH, project=story.project)
            # logger.debug("TrashBin iteration founded %s " %iteration)
        except ObjectDoesNotExist:
            iteration = Iteration.objects.create(
                name='Trash Bin',
                project=story.project,
                iteration_type=Iteration.ITERATION_TRASH,
                hidden=True,
                include_in_velocity=False
            )
            logger.debug("New TrashBin iteration created %s " %iteration)

        if iteration.project != project:
            raise ValidationError("Organization and project don't match")

        iterationChanged = story.iteration != iteration

        if iterationChanged:
            logger.debug("Moving story to Trash and removing it from release and epics.")
            story.iteration = iteration
            story.release = None
            story.epic = None
            _moveStoryOutOfCell(story, project, request.user)
            story.save()

        self._indexStory(story)

    def _clone_time_entries(self, request, project, story, task_id):
        entries = TimeEntry.objects.filter(project=project, task_id=task_id)
        new_entries = []
        for entry in entries:
            entry.pk = None
            entry.task_id = None
            entry.story_id = story.id
            entry.save()
            new_entries.append(entry)
        entries.delete()
        return new_entries

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def create(self, request, organization_slug, project_slug, iteration_id):
        data = request.data
        org, project = checkOrgProject(request, organization_slug, project_slug, True)
        realtime_util.lock_realtime_project(project)
        try:

            iteration = project.iterations.get(id=iteration_id)

            story = Story(project=project, iteration=iteration)
            story.rank = 500000
            story.local_id = project.getNextId()
            story.project = project
            story.creator = request.user
            story.iteration = iteration

            if "relativeRank" in data:
                    modifiedOthers, modifiedList = setRelativeRank(story, iteration, data["relativeRank"])
            else:
                others = iteration.stories.all().order_by("rank")
                if others.count() == 0:
                    story.rank = 500000
                    modifiedOthers = False
                else:
                    # firstRank = others[0].rank
                    # story.rank
                    modifiedOthers, modifiedList = reorderStory(story, -1, others[0].id, iteration)

            result = self._updateStory(story, data, project, request)

            #check if we got request to promote task as a story
            if "fromTaskId" in data and data["fromTaskId"] > 0:
                self._clone_time_entries(request, project, story, data["fromTaskId"])

            if story.release:
                try:
                    projects_tasks.queueMacroStatsCalc(story.id, None)
                    max_rank = story.release.stories.all().aggregate(Max('release_rank'))['release_rank__max']
                    if max_rank:
                        story.release_rank = max_rank + 5000
                        story.save()
                except:
                    pass

            if story.epic:
                calculateEpicStats(story.epic)
                try:
                    max_rank = story.epic.stories.all().aggregate(Max('epic_rank'))['epic_rank__max']
                    if max_rank:
                        story.epic_rank = max_rank + 5000
                        story.save()
                except:
                    pass

            if story.cell is None and story.iteration.iteration_type == Iteration.ITERATION_BACKLOG:
                kanban_manager._create_story_history(story)

            if modifiedOthers:
                story.reorderResults = {'modifiedOther': modifiedOthers, 'newRank': story.rank, 'storiesModified': modifiedList}

            if settings.USE_QUEUE:
                projects_tasks.sendStoryAddedSignals.apply_async((story.id, request.user.id), countdown=3)
            else:
                projects_tasks.sendStoryAddedSignals(story.id, request.user.id)

            self._checkForComment(story, data, request)

            self._checkForTempAttachments(story, project, request)

            self._checkForDependencies(story, data, request)

            self._checkForRisks(story, data, request)

            # projects_tasks.queueUpdateSolr(story.id)

            self._indexStory(story)

            return result
        finally:
            realtime_util.unlock_realtime_project(project, delay=5)

    def _indexStory(self, story):
        projects_tasks.queueUpdateSolr(story.id)
        # try:
        #     index = connections['default'].get_unified_index().get_index(Story)
        #     index.update_object(story)
        # except:
        #     logger.error("Could not index card")

    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug,
             iteration_id=None, story_id=None, category=None,
             epic_id=None, iteration_ids=None, release_id=None, archive=0,
             assignment_id=None):

        org, project = checkOrgProject(request, organization_slug, project_slug)

        if release_id is not None:
            if int(release_id) > 0:
                release = Story.objects.get(project__organization=org, id=release_id)
                q = project.stories.filter(release=release) \
                        .select_related("epic", "creator", "project", "cell", "release") \
                        .prefetch_related("story_tags__tag", "assignee", "extra_attributes", "labels").order_by("rank")
            else:
                q = project.stories.filter(release=None) \
                        .select_related("epic", "creator", "project", "cell", "release") \
                        .prefetch_related("story_tags__tag", "assignee", "extra_attributes", "labels").order_by("rank")
            if iteration_id is not None:
                q = q.filter(iteration_id=iteration_id)
            return q
        elif iteration_ids is not None:
            iteration_ids = iteration_ids.split(",")
            return project.stories.filter(project=project, iteration_id__in=iteration_ids).\
                select_related("epic", "creator", "project", "cell", "release").\
                prefetch_related("story_tags__tag", "assignee", "extra_attributes").\
                order_by("rank")
        elif epic_id is not None and int(epic_id) is -1:
            archive_iteration = kanban_manager.getArchiveIteration(project)
            if iteration_id is not None:
                return project.stories\
                    .filter(epic_id__isnull=True, iteration_id = iteration_id)\
                    .select_related("epic", "creator", "project", "cell", "release")
            if int(archive) is 0:
                return project.stories\
                    .filter(epic_id__isnull=True)\
                    .exclude(iteration_id=archive_iteration.id)\
                    .select_related("epic", "creator", "project", "cell", "release")
            else:
                return project.stories\
                    .filter(epic_id__isnull=True)\
                    .select_related("epic", "creator", "project", "cell", "release")

        elif epic_id is not None:
            epic = project.epics.get(id=epic_id)
            if iteration_id is None:
                return epic.stories\
                    .all()\
                    .select_related("epic", "creator", "project", "cell", "release")
            else:
                return epic.stories.filter(iteration_id=iteration_id)
        elif story_id is not None:
            story = Story.objects.get(id=story_id)
            if story.project != project:
                raise PermissionDenied("You don't have access to that Project")
            return story
        elif iteration_id is not None:
            iteration = project.iterations.get(id=iteration_id)
            return iteration.stories.all()\
                .select_related("epic", "creator", "project", "cell", "release")\
                .prefetch_related("story_tags__tag", "assignee", "extra_attributes", "labels").order_by("rank")
        else:
            return paginate(Story.objects.select_related("epic", "creator", "project", "cell").filter(project=project).prefetch_related("story_tags__tag","assignee","extra_attributes"), request)



class MoveStoryHandler(BaseHandler):
    allowed_methods = ('PUT',)

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def update(self, request, organization_slug, project_slug, story_id):
        data = request.data
        org, project = checkOrgProject(request, organization_slug, project_slug, True)

        story = Story.objects.get(id=story_id)

        # Save a copy so we can get diffs at the end.
        old_story = story.__dict__.copy()

        if story.project != project:
            raise ValidationError("Organization and project don't match")

        destinationProject = Project.objects.get(slug=data['project_slug'])
        destinationIteration = destinationProject.iterations.get(id=data['iteration_id'])
        try:
            destinationCell = destinationProject.boardCells.get(id=data['cell_id'])
        except (ObjectDoesNotExist, KeyError) as e:
            destinationCell = None

        try:
            release_id = data['release_id']
            release = Story.objects.get(id=release_id, project__organization=org)
            story.release = release
        except KeyError:
            pass
        except ObjectDoesNotExist:
            story.release = None

        if not has_write_access(destinationProject, request.user):
            raise PermissionDenied()

        if destinationProject.organization != org:
            raise ValidationError("Can not move a story between organizations")

        sameProject = story.project == destinationProject
        sameIteration = story.iteration == destinationIteration

        moveOutOfCell = False

        if not sameProject:
            moveOutOfCell = True
            story.epic = None
            story.cell = None
            story.epic_label = None
            story.project = destinationProject
            story.local_id = destinationProject.getNextId()
            transferLabels(story, destinationProject)
            transferTags(story, destinationProject)
            transferBlockers(story, destinationProject)
            transferRelease(story, destinationProject)

        if not sameIteration:
            story.iteration = destinationIteration
            moveOutOfCell = moveOutOfCell or (destinationIteration.iteration_type != Iteration.ITERATION_WORK)

        if moveOutOfCell:
            # When moving into backlog/archive or when moving to a different project,
            # we need to add a CellMovement record that takes it out of it's current cell
            kanban_manager.moveStoryOntoCell(story, destinationCell, request.user)

        story.save()
        kanban_manager.moveStoryOntoDefaultCell(story, destinationProject, request.user)

        diffs = utils.model_differences(old_story, story.__dict__, ["modified"], dicts=True)
        signals.story_updated.send(sender=request, story=story, diffs=diffs, user=request.user)

        broadcastIterationCounts(project)

        if not sameProject:
            # Moved to a new project, equivalent to deleting it in the old and creating it in the new
            realtime_util.send_story_delete(project, story.id)
            realtime_util.send_story_created(destinationProject, story)
        elif not sameIteration:
            # Moved within a project, update the iteration and cell
            realtime_util.send_story_patch(project, story, {'iteration_id': story.iteration_id})
            # rebuild Cell Related System Risks Cache
            projects_tasks.rebuildCellHeaderRisks.apply_async((project, story.iteration_id), countdown=5)
            projects_tasks.rebuildCellHeaderRisks.apply_async((project, old_story['iteration_id']), countdown=5)

        projects_tasks.queueUpdateSolr(story.id)
        return story


class CurrentStoriesHandler(BaseHandler):
    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug):
        org = Organization.objects.get(slug=organization_slug)
        if not org.hasReadAccess(request.user):
            raise PermissionDenied("You don't have access to that Organization")
        return getAssignedStories(request.user, org)


class ConvertToEpicHandler(BaseHandler):
    allowed_methods = ('POST',)

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def create(self, request, organization_slug, project_slug, story_id):
        org, project = checkOrgProject(request, organization_slug, project_slug, True)
        story = project.stories.get(id=story_id)
        parentEpic = story.epic
        epic = Epic(summary=strip_tags(story.summary),
                    local_id=project.getNextEpicId(),
                    parent=parentEpic,
                    detail=strip_tags(story.detail),
                    points=story.points,
                    project=story.project)
        epic.save()
        children = []
        rank = story.rank
        for task in story.tasks.all():
            child = Story(project=project, iteration=story.iteration)
            child.summary = task.summary
            child.local_id = project.getNextId()
            child.creator = request.user
            child.epic = epic
            child.rank = rank
            child.cell = story.cell
            rank += 10
            child.save()
            if task.assignee is not None:
                child.assignee.add(task.assignee)
            children.append(child)
            projects_tasks.sendStoryAddedSignals.apply_async((child.id, request.user.id), countdown=3)
        story.sync_queue.clear()
        story.delete()

        return {'epic':epic, 'child_stories':children}


class DuplicateStoryHandler(BaseHandler):
    allowed_methods = ('POST',)

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def create(self, request, organization_slug, project_slug, story_id):
        org, project = checkOrgProject(request, organization_slug, project_slug, True)
        story = project.stories.get(id=story_id)


        dupe = Story()
        fields = (
            'rank',
            'tags',
            'summary',
            'detail',
            'modified',
            'points',
            'iteration',
            'project',
            'category',
            'extra_1',
            'extra_2',
            'extra_3',
            'epic',
            'business_value',
            'estimated_minutes',
            'time_criticality',
            'risk_reduction',
            'release')
        for field in fields:
            setattr(dupe, field, getattr(story, field))
        dupe.creator = request.user
        dupe.local_id = story.project.getNextId()
        dupe.save()  # Need a primary id to assign assignees..

        for assignee in story.assignee.all():
            dupe.assignee.add(assignee)

        for label in story.labels.all():
            dupe.labels.add(label)

        for task in story.tasks.all():
            dupeTask = Task(story=dupe,
                            summary=task.summary,
                            assignee=task.assignee,
                            order=task.order,
                            tags=task.tags,
                            estimated_minutes=task.estimated_minutes
                            )
            dupeTask.save()

        dupe.resetCounts()  # implicit save

        if story.cell:
            kanban_manager.moveStoryOntoCell(dupe, story.cell, request.user)

        if settings.USE_QUEUE:
            projects_tasks.sendStoryAddedSignals.apply_async((dupe.id, request.user.id), countdown=3)
        else:
            projects_tasks.sendStoryAddedSignals(dupe.id, request.user.id)

        return dupe

class SearchHandler(BaseHandler):
    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug=None, iteration_id=None):
        if project_slug:
            return self.projectSearch(request, organization_slug, project_slug, iteration_id)

        return self.organizationSearch(request, organization_slug)

    def organizationSearch(self, request, organization_slug):
        if request.GET.get("q","") == "":
            logger.info("Ignoring empty search")
            return paginate([],request)


        organization = Organization.objects.get(slug=organization_slug)
        query_string = request.GET.get("q")
        q = search_views.parseQuery(query_string)
        q["order"] = ("-created",);
        query = search_views.performSearch(q, organization, None, None, True)

        results = query


        search_results = []
        for r in results:
            if r == None:
                continue
            story = r.object
            if has_read_access(story.project, request.user) and story.iteration.iteration_type != Iteration.ITERATION_TRASH:
                search_results.append(story)
            # support pagination on UI
            #if len(search_results) > 99:
            #    break

        return paginate(search_results, request, storyWithIterationHandler)

    def projectSearch(self, request, organization_slug, project_slug, iteration_id=None):
        org, project = checkOrgProject(request, organization_slug, project_slug)

        # check if we have to filter in iteration ids for project Search
        try:
            iteration_str = re.search(r'iterations: ([0-9]+.+),', str(request.GET.get("q",""))).group(1)
            iteration_ids = re.sub('-', ',', iteration_str)
        except AttributeError:
            iteration_ids = None

        query = re.sub(r'iterations: ([0-9]+.+)', '', str(request.GET.get("q","")))

        query = search_views.parseQuery( query )
        search_backlog = request.GET.get("backlog","true") == "true"
        search_archive = request.GET.get("archive","true") == "true"

        if iteration_id:
            iterationIdList = iteration_id.split(",")
            iterations = project.iterations.filter(id__in=iterationIdList)
            search_results = []
            ids = set()
            for r in search_views.performSearch(query, org, project, iterations, True):
                if not r.id in ids:
                    # I was getting duplicate results from haystack here, and they were two copies of the same record.
                    search_results.append(r.object)
                    ids.add(r.id)
                else:
                    logger.info("Duplicate search result?")
            if request.GET.get("cardPicker",None) != 'true':
                return search_results
            return paginate(search_results, request, storyWithIterationHandler)  # no need to paginate searches of a single iteration.
        else:
            search_results = []
            # filter out Trash Iterations
            iterations = project.iterations.all().exclude(iteration_type = Iteration.ITERATION_TRASH)
            
            # filter out user submitted Iterations
            if iteration_ids is not None:
                iterations =  project.iterations.filter(Q(id__in = iteration_ids.split(",")) |\
                                                        Q(iteration_type = Iteration.ITERATION_BACKLOG) |\
                                                        Q(iteration_type = Iteration.ITERATION_ARCHIVE))
            # filter out Backlog if not needed
            if not search_backlog:
                iterations = iterations.filter(~Q(iteration_type = Iteration.ITERATION_BACKLOG))
            # filter out Archive if not Needed
            if not search_archive:
                iterations = iterations.filter(~Q(iteration_type = Iteration.ITERATION_ARCHIVE))

            for r in search_views.performSearch(query, org, project, iterations, True):
                if r.object.iteration.iteration_type != Iteration.ITERATION_TRASH:
                    search_results.append(r.object)

        return paginate(search_results, request, storyWithIterationHandler)


class MyStoryHandler(BaseHandler):
    allowed_methods = ("GET",)


    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug=None, iteration_id=None):
        organization = Organization.objects.get(slug=organization_slug)
        if not organization.hasReadAccess(request.user):
            raise PermissionDenied("You don't have access to that organization")

        return self._getAssignedStories(request.user, organization)

    @staticmethod
    def _getAssignedStories(user, organization):
        # Stories directly assigned
        # Also, ignoring stories more than 6 months old
        sixmonthsago = datetime.date.today() - datetime.timedelta(days=6*30)
        today = tz.today(organization)
        assigned = Story.objects.filter(# Either assigned to user, or has a task assigned.
                                        Q(assignee=user) | Q(tasks__assignee=user),
                                        # Either a current iteration, or a dateless iteration or continous iteration...
                                        (Q(iteration__start_date__lte=today) & Q(iteration__end_date__gte=today)) | Q(iteration__start_date=None)\
                                        | (Q(iteration__end_date=None) & Q(iteration__start_date__lte=today)),
                                        # Recently modified
                                        modified__gt=sixmonthsago,
                                        # In this organization
                                        project__organization=organization,
                                        project__active=True,
                                        # In a work iteration (not archive/backlog)
                                        iteration__iteration_type=Iteration.ITERATION_WORK
                                        ).distinct()

        return assigned.order_by("project__name") \
                       .select_related("epic","creator","project") \
                       .prefetch_related("story_tags__tag","assignee","extra_attributes")


class StoryWithoutAssigneeHandler(StoryHandler):
    model = None

    @staticmethod
    def assignee(story):
        return []

storyWithoutAssigneeHandler = StoryWithoutAssigneeHandler()

class StoryAgingHandler(BaseHandler):
    allowed_methods = ('GET', 'POST')

    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug, story_id):
        org, project = checkOrgProject(request, organization_slug, project_slug, False)
        story = Story.objects.get(id=story_id)
        if story.project != project:
            raise ValidationError("Organization and project don't match")

        aging_info = kanban_manager.get_aging_info(story)
        return tuple(aging_info)


    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def create(self, request, organization_slug, project_slug, story_id):
        org, project = checkOrgProject(request, organization_slug, project_slug, True)
        story = project.stories.get(id=story_id)
        story.resetAgeHours()
        realtime_util.send_story_patch(project, story, {"age_hours": 0})
        diffs = {'aging_reset': ('', 'Reset card aging')}
        signals.story_updated.send(sender=request, story=story, diffs=diffs, user=request.user)
        return "updated"


class TimelineStoryHandler(BaseHandler):
    allowed_methods = ('GET', )

    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug, iteration_id = None):
        org, project = checkOrgProject(request, organization_slug, project_slug, False)
        project_cells = project.boardCells.filter(time_type = BoardCell.DONE_TIME).order_by("x")
        try:
            done_cell = project_cells[0]
        except:
            return []
    
        stories = []

        if iteration_id is not None:
            stories = project.stories.filter(project=project, iteration_id=iteration_id). \
                        order_by("rank").prefetch_related('assigned_to')
        else:
            stories = project.stories.filter(project=project).\
                        order_by("rank").prefetch_related('assigned_to')
        
        data = []

        done_dates = self._get_done_dates(done_cell, iteration_id)
        uncommitted_dates = self._get_uncommitted_dates(iteration_id)

        for story in stories:
            try:
                done_on = done_dates[story.id].created
            except:
                done_on = None
            try:
                uncommitted_on = uncommitted_dates[story.id].created
            except:
                uncommitted_on = None
            
            try:
                assigned = story.assigned_to.values('assigned').all().order_by("assigned")[0]
                committed_on = assigned["assigned"]
            except:
                committed_on = None

            data.append({
                        'story_id': story.id,
                        'uncommitted_date': uncommitted_on,
                        'committed_date': committed_on,
                        'done_date': done_on
            })

        return data

    def _get_done_dates(self, done_cell, iteration_id):
        done_dates = CellMovement.objects.filter(cell_to_id = done_cell.id,related_iteration_id = iteration_id). \
                    order_by("story_id", "-created")
        
        dates = {}
        for date in done_dates:
            if date.story_id not in dates:
                dates[date.story_id] = date
        
        return dates;
    
    def _get_uncommitted_dates(self, iteration_id):
        uncommitted_dates = CellMovement.objects.filter(related_iteration_id = iteration_id). \
                    order_by("story_id", "created")
        
        dates = {}
        for date in uncommitted_dates:
            if date.story_id not in dates:
                dates[date.story_id] = date
        
        return dates;

class MiniStoryHandler(BaseHandler):
    """
    MiniStory Handler to provide minimum story data
    """
    allowed_methods = ('GET', )
    fields = ("id",
            "number",
            "rank",
            "created",
            "modified",
            "summary",
            "iteration_id",
            "iteration_name",
            "iname",
            "project_id",
            "project_slug",
            'prefix',
            'release',
            'global_backlog_card')

    @staticmethod
    def global_backlog_card(story):
        if story.project.project_type == Project.PROJECT_TYPE_BACKLOG_ONLY:
            return {"type": story.project.work_item_name}
        else:
            return None
    
    @staticmethod
    def iteration_name(story):
        return story.iteration.name

    @staticmethod
    def number(story):
        return story.local_id

    @staticmethod
    def prefix(story):
        return story.project.prefix

    @staticmethod
    def project_slug(story):
        return story.project.slug

    @staticmethod
    def release(story):
        if story.release_id is None:
            return None
        return {
            'id': story.release.id,
            'number': story.release.local_id,
            'iteration_id': story.release.iteration_id,
            'project_slug': story.release.project.slug,
            'project_prefix': story.release.project.prefix,
            'summary': story.release.summary
        }

    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug=None,
             iteration_id=None, story_id=None, category=None,
             epic_id=None, iteration_ids=None, release_id=None, archive=0,
             assignment_id=None, portfolio_root_slug=None):
        
        load_active_only = request.GET.get("active_only", "false") == "true"

        if project_slug is not None:
            org, project = checkOrgProject(request, organization_slug, project_slug)
        else:
            org = Organization.objects.get(slug=organization_slug)
            if not org.hasReadAccess(request.user):
                raise PermissionDenied("You don't have access to that Organization")

        if release_id is not None:
            release = Story.objects.get(project__organization=org, id=release_id)
            if project_slug is not None:
                q = project.stories.filter(release=release) \
                    .select_related("project", "iteration").order_by("rank")
            else:
                q = Story.objects.filter(release=release).select_related("project").order_by("rank")
            if iteration_id is not None:
                q = q.filter(iteration_id=iteration_id)

            if load_active_only is True:
                # load stories not archived or not in archied iterations
                q = q.filter((Q(iteration__iteration_type=Iteration.ITERATION_BACKLOG)\
                            |Q(iteration__iteration_type=Iteration.ITERATION_WORK)),\
                            iteration__hidden = False)
            return q
        elif iteration_ids is not None:
            iteration_ids = iteration_ids.split(",")
            return project.stories.filter(project=project, iteration_id__in=iteration_ids)\
                                        .select_related("project", "iteration").order_by("rank")
        elif epic_id is not None and int(epic_id) is -1:
            archive_iteration = kanban_manager.getArchiveIteration(project)
            if iteration_id is not None:
                return project.stories\
                    .filter(epic_id__isnull=True, iteration_id = iteration_id)\
                    .select_related("project", "iteration")
            if int(archive) is 0:
                return project.stories\
                    .filter(epic_id__isnull=True)\
                    .exclude(iteration_id=archive_iteration.id)\
                    .select_related("project", "iteration")
            else:
                return project.stories\
                    .filter(epic_id__isnull=True)\
                    .select_related("project", "iteration")

        elif epic_id is not None:
            epic = project.epics.get(id=epic_id)
            if iteration_id is None:
                return epic.stories\
                    .all()\
                    .select_related("project", "iteration")
            else:
                return epic.stories.filter(iteration_id=iteration_id)
        elif story_id is not None:
            story = Story.objects.get(id=story_id)
            if story.project != project:
                raise PermissionDenied("You don't have access to that Project")
            return story
        elif iteration_id is not None:
            iteration = project.iterations.get(id=iteration_id)
            return iteration.stories.all()\
                .select_related("project", "iteration").order_by("rank")
        else:
            return Story.objects.select_related("project", "iteration")\
                                .filter(project=project)

