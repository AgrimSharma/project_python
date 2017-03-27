from common import *
from django.core.cache import cache
from django.db.models import Max, Q, Count, Case, When, IntegerField,Value

import json
import datetime
import math

import apps.kanban.managers as kanban_manager
import apps.kanban.stats as kstats
import apps.projects.org_backlog as org_backlog_manager
import apps.projects.managers as project_manager
from apps.kanban.models import Workflow, KanbanStat, BoardCell
from apps.projects.models import Iteration, MilestoneAssignment, PointScale, Story, ProgramIncrement
from apps.favorites.models import Favorite
from apps.projects.tasks import updateProjectIndexes

CACHE_PROJECTSTATS_SECONDS = 600

class ProjectHandler(BaseHandler):
    allowed_methods = ('GET', 'PUT', 'POST', 'DELETE')
    model = Project
    exclude = ('status_names', 'creator', 'private', 'token', 'organization')
    write_fields = ("name",
                      "description",
                      "point_scale_type",
                      "category",
                      "use_extra_1",
                      "use_extra_2",
                      "use_extra_3",
                      "extra_1_label",
                      "extra_2_label",
                      "extra_3_label",
                      "statuses",
                      "members",
                      "velocity_type",
                      "render_mode",
                      "active",
                      "shared",
                      "time_tracking_mode",
                      "work_item_name",
                      "folder_item_name",
                      "color",
                      "icon",
                      "aging_display",
                      "warning_threshold",
                      "critical_threshold",
                      "use_time_crit",
                      "use_risk_reduction",
                      "use_points",
                      "use_time_estimate",
                      "use_due_date",
                      "business_value_mode",
                      "tab_sentiments",
                      "tab_board",
                      "tab_teamplanning",
                      "tab_dependencies",
                      "tab_chat",
                      "tab_planning",
                      "tab_risks",
                      "tab_timeline",
                      "tab_milestones",
                      "duedate_warning_threshold",
                      "continuous_flow_iteration_id",
                      "auto_archive_iterations",
                      "vision")
    fields = ("url",
              "id",
              "name",
              "slug",
              "description",
              "velocity",
              "created",
              "iterations_left",
              "creator_id",
              "tags",
              "icon",
              "alltags",
              "point_scale_type",
              "point_scale",
              "category",
              "use_extra_1",
              "use_extra_2",
              "use_extra_3",
              "extra_1_label",
              "extra_2_label",
              "extra_3_label",
              "use_time_crit",
              "use_risk_reduction",
              "use_points",
              "use_time_estimate",
              "use_due_date",
              "burnup_reset_date",
              "burnup_reset",
              "statuses",
              "card_types",
              "members",
              "task_statuses",
              "kanban_iterations",
              "project_type",
              "render_mode",
              "active",
              "watched",
              "stats",
              "labels",
              "personal",
              "velocity_type",
              "default_cell_id",
              "story_queue_count",
              "releases",
              "milestone_counts",
              "shared",
              "time_tracking_mode",
              "color",
              "work_item_name",
              "folder_item_name",
              "business_value_mode",
              "aging_display",
              "warning_threshold",
              "critical_threshold",
              "portfolio_id",
              "portfolio_slug",
              "portfolio_level_id",
              ("parents", ("id", "name", "slug", "color", "icon", "work_item_name", "portfolio_level_id", "active")),
              ("children", ("id", "name", "slug", "color", "icon", "work_item_name", "portfolio_level_id", "active")),
              "prefix",
              "prefix_error",
              "tab_sentiments",
              "tab_board",
              "tab_teamplanning",
              "tab_dependencies",
              "tab_chat",
              "tab_planning",
              "tab_risks",
              "tab_milestones",
              "tab_timeline",
              "children_count",
              "duedate_warning_threshold",
              "vision",
              "continuous_flow",
              "continuous_flow_iteration_id",
              "auto_archive_iterations"
    )

    @staticmethod
    def continuous_flow(project):
        return project.continuous_flow_iteration is not None

    @staticmethod
    def children_count(project):
        return project.children.count()

    @staticmethod
    def portfolio_id(project):
        if project.portfolio_level is None:
            return None
        return project.portfolio_level.portfolio_id

    @staticmethod
    def portfolio_slug(project):
        return project.portfolio_level.portfolio.root.slug if project.portfolio_level is not None else None

    @staticmethod
    def milestone_counts(project):
        return {
            'active': MilestoneAssignment.objects.filter(assigned_project=project, active=True).count(),
            'inactive': MilestoneAssignment.objects.filter(assigned_project=project, active=False).count(),
        }

    @staticmethod
    def releases(project):
        release_projects = list(project.parents.all())
        if len(release_projects) == 0:
            return []
        return [{'id': s.id,
                 'number': s.local_id,
                 'iteration_id': s.iteration_id,
                 'project_slug': s.project.slug,
                 'project_prefix': s.project.prefix,
                 'summary': s.summary} for s in Story.objects.filter(project__in=release_projects)
                                                    .exclude(iteration__iteration_type=Iteration.ITERATION_TRASH)
                                                    .select_related("project")
                                                    .order_by("local_id")]

    @staticmethod
    def optimised_releases(project):
        release_projects = list(project.parents.all().values_list('id'))
        if len(release_projects) == 0:
            return []
        return [{'id': s.id,
                 'number': s.local_id,
                 'iteration_id': s.iteration_id,
                 'project_slug': s.project.slug,
                 'project_prefix': s.project.prefix,
                 'summary': s.summary} for s in Story.objects.filter(Q(project_id__in=release_projects))
                                                    .exclude(iteration__iteration_type=Iteration.ITERATION_TRASH)
                                                    .select_related("project")
                                                    .order_by("local_id")]


    @staticmethod
    def story_queue_count(project):
        return project.story_queue.filter(archived=False).count()

    @staticmethod
    def default_cell_id(project):
        if project.default_cell is None:
            return None
        return project.default_cell_id


    @staticmethod
    def tags(project):
        return project.tags.values("name").distinct()

        # d = {}
        # for obj in project.tags.all():
        #     d[obj.name] = obj
        # return d.values()

    @staticmethod
    def alltags(project):
        return project.tags.all()
    @staticmethod
    def labels(project):
        # To make the prefetch_releated on labels work correctly, I had to do it this way.
        # , ("id", "name", "color"))
        return [{"id":l.id, "name":l.name, "color":l.color} for l in project.labels.all()]

    @staticmethod
    def kanban_iterations(project):
        try:
            if project.project_type == Project.PROJECT_TYPE_SCRUM:
                return {}
            return {
                "backlog": project.get_default_iteration().id,
                "archive": kanban_manager.getArchiveIteration(project).id
            }
        except AttributeError:
            return {}

    @staticmethod
    def members(project):
        return project.assignable_members()

    @staticmethod
    def point_scale(project):
        return project.getPointScale()

    @staticmethod
    def url(project):
        return project.get_absolute_url()

    @staticmethod
    def task_statuses(project):
        return list(project.task_statuses())

    @staticmethod
    def card_types(project):
        return list(project.cardTypes())

    @staticmethod
    def statuses(project):
        try:
            return list(project.statuses())
        except:
            return []

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def delete(self, request, organization_slug, project_slug):
        org, project = checkOrgProject(request, organization_slug, project_slug)
        if not org.hasStaffAccess(request.user):
            raise PermissionDenied()
        project_manager.delete_project(project)
        return {}

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def create(self, request, organization_slug):
        org = Organization.objects.get(slug=organization_slug)
        if not org.hasStaffAccess(request.user):
            raise PermissionDenied()

        data = request.data

        parents = data.get('parents', None)
        if parents is not None:
            parent_ids = (p['id'] for p in parents)
        else:
            parent_ids = []

        project = project_manager.create_project(
            data['name'],
            org,
            request.user,
            False,
            data.get('teams',[]),
            data.get('project_type', 1),
            0,
            parent_ids,
            data.get("work_item_name", "Card"),
            data.get("folder_item_name", "Epic")
        )

        return project

    def _update_project(self, project, data, request):

        if "parents" in data and data['parents'] is not None:
            parent_ids = [p['id'] for p in data['parents']]
            parents = Project.objects.filter(id__in=parent_ids, organization_id=project.organization_id)
            org_backlog_manager.set_project_parents(project, parents)

        for field in ProjectHandler.write_fields:
            if field in data:
                setattr(project, field, data[field])

        if "default_cell_id" in data:
            try:
                cell = project.boardCells.get(id=data['default_cell_id'])
                project.default_cell = cell
            except:
                pass

        if "default_workflow" in data:
            # Temporary measure.  Can be removed once the backbone board editor goes away.
            id = data['default_workflow']
            Workflow.objects.filter(project=project, id=id).update(default=True)
            Workflow.objects.filter(project=project).exclude(id=id).update(default=False)

        if "task_statuses" in data:
            project.task_status_names = ""
            for i in range(10):
                project.task_status_names += "%-10s" % data["task_statuses"][i]

        if "continuous_flow_iteration_id" in data and data["continuous_flow_iteration_id"] is not None and\
            "continuous_flow_destination_id" in data:
            try:
                continuous_iteration = project.iterations.filter(id = int(data["continuous_flow_iteration_id"]))[0]
                if data["continuous_flow_destination_id"] is not None:
                    destination_iteration = project.iterations.filter(id = int(data["continuous_flow_destination_id"]))[0]
                else:
                    destination_iteration = continuous_iteration
                project_manager.addContinuousFlowIteration(request, project, continuous_iteration.id, destination_iteration.id)
            except IndexError:
                pass


    def _update_project_prefix(self, project, prefix):
        try:
            Project.objects.exclude(id=project.id).get(prefix=prefix, organization = project.organization)
            return False
        except Project.DoesNotExist:
            project.prefix = prefix[:2]
            project.save()
            # update project Indexes for new prefix search
            updateProjectIndexes.delay(project.slug)
            return True

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def update(self, request, organization_slug, project_slug, action=None):
        org, project = checkOrgProject(request, organization_slug, project_slug)

        data = request.data

        if not has_admin_access(project, request.user):
            raise PermissionDenied("You don't have access to that Project")

        self._update_project(project, data, request)
        project.full_clean()
        project.save()

        if "prefix" in data and data["prefix"].strip() != "" and len(data["prefix"]) == 2 and project.prefix != data["prefix"]:
            if not self._update_project_prefix(project, data["prefix"]):
                project.prefix_error = True

        project.watched = Favorite.getFavorite(request.user, project) is not None

        if project.watched or request.GET.get('stats', 'false') == 'True':
            self.addStats([project])

        return project

    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug=None):
        org = Organization.objects.get(slug=organization_slug)
        if not org.hasReadAccess(request.user):
            raise PermissionDenied("You don't have access to that Organization")

        if project_slug == '__releases__':  # __releases__ is a special slug
            project = org.projects.filter(project_type=Project.PROJECT_TYPE_PORTFOLIO, active=True)[0]
            # Everyone in the organization can see the list of releases, no need for this check.
            # if not has_read_access(project, request.user):
            #     raise PermissionDenied("You don't have access to that Project")
            return project
        elif project_slug:
            project = Project.objects.get(slug=project_slug)
            if not has_read_access(project, request.user):
                raise PermissionDenied("You don't have access to that Project")
            if project.organization != org:
                raise ValidationError("Organization and project don't match")

            project.watched = Favorite.getFavorite(request.user, project) is not None
            self.addStats([project], request.GET.get('stats', "false") == "true")

            return project
        else:
            # projects fields:
            # abandoned, active, attachmentextra, basecampcredentials,
            # basecampetags, boardCells, burnup_reset, burnup_reset_date,
            # card_types, categories, category, cfdcache, chatmessage, created,
            # creator, description, emailnotificationqueue, epics, extra_1_label,
            # extra_2_label, extra_3_label, extra_attributes, extras, favorite,
            # githubbinding, githubcredentials, githublog, graphics, has_iterations_hidden,
            # headers, id, images, iterations, iterations_left, kanbanstat, labels, live_updates,
            # log_items, member_users, members, name, newsItems, organization, personal,
            # point_scale_type, points_log, policies, portfolio_mappings, private, project_type,
            # projectemailsubscription, releases, render_mode, slug, status_names, stories,
            # story_minutes, story_queue, syncronizationqueue, tags, task_status_names, teams,
            # timeallocation, timeentry, token, use_extra_1, use_extra_2, use_extra_3,
            # velocity, velocity_iteration_span, velocity_type, workflows

            if org.hasStaffAccess(request.user):
                projects = org.projects\
                    .filter(Q(personal=False) | Q(creator=request.user, personal=True))\
                    .select_related("organization","portfolio_level").prefetch_related("labels", "teams", "teams__members")
            else:
                projects = get_users_cached_projects(org, request.user)

            for project in projects:
                project.watched = Favorite.getFavorite(request.user, project) is not None

            if request.GET.get("stats", "false") == "true":
                projects = self.addStats(projects, True, request.user)
            
            return projects


    def addStats(self, projects, force=False, user=None):
        for project in projects:
            if project.watched or force:
                # moved logic to manager and return cached value if there
                stats = project_manager.get_kanban_stats(project)
                project.stats = stats

        return projects


class DashbaordProjectsHandler(BaseHandler):
    allowed_methods = ('GET',)
    fields = ("url",
              "id",
              "name",
              "slug",
              "velocity",
              "creator_id",
              "icon",
              "category",
              "project_type",
              "active",
              "watched",
              "stats",
              "personal",
              "velocity_type",
              "shared",
              "color",
              "work_item_name",
              "folder_item_name",
              "business_value_mode",
              "portfolio_id",
              "portfolio_slug",
              "portfolio_level_id",
              "prefix",
              "prefix_error",
              "children_count"
            )

    @staticmethod
    def url(project):
        return project.get_absolute_url()

    @staticmethod
    def children_count(project):
        return project.children.count()

    @staticmethod
    def portfolio_id(project):
        if project.portfolio_level is None:
            return None
        return project.portfolio_level.portfolio_id

    @staticmethod
    def portfolio_slug(project):
        return project.portfolio_level.portfolio.root.slug if project.portfolio_level is not None else None

    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug=None):
        org = Organization.objects.get(slug=organization_slug)
        if not org.hasReadAccess(request.user):
            raise PermissionDenied("You don't have access to that Organization")
        
        if org.hasStaffAccess(request.user):
                projects = org.projects\
                .filter(Q(personal=False) | Q(creator=request.user, personal=True))\
                .select_related("organization","portfolio_level")
        else:
            projects = get_users_cached_projects(org, request.user)

        for project in projects:
            project.watched = Favorite.getFavorite(request.user, project) is not None

        if request.GET.get("stats", "false") == "true":
            projects = self.addStats(projects, True, request.user)
        
        return projects
    
    def addStats(self, projects, force=False, user=None):
        for project in projects:
            if project.watched or force:
                # moved logic to manager and return cached value if there
                stats = project_manager.get_kanban_stats(project)
                project.stats = stats
        return projects

class ProjectAccessHandler(BaseHandler):
    allowed_methods = ('GET',)
    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug ):
        org = Organization.objects.get(slug=organization_slug)
        if not org.hasReadAccess(request.user):
            raise PermissionDenied("You don't have access to that Organization")

        project = Project.objects.get(slug=project_slug)
        if not has_read_access(project, request.user):
            raise PermissionDenied("You don't have access to that Project")
        if project.organization != org:
            raise ValidationError("Organization and project don't match")
        access_type = "read"
        if has_admin_access(project, request.user):
            access_type = "admin"
        elif has_write_access(project, request.user):
            access_type = "write"
        return {'access': access_type, 'project': project}


class PointScaleHandler(BaseHandler):
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE',)

    fields = ("id", "scale_value",)

    @staticmethod
    def scale_value(pointscale):
        return json.loads(pointscale.value)

    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug ):
        org, project = checkOrgProject(request, organization_slug, project_slug, False)

        pointScales = PointScale.objects.filter(project=project)

        return pointScales

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def create(self, request, organization_slug, project_slug):
        data = request.data
        org, project = checkOrgProject(request, organization_slug, project_slug, True)

        point_scale = PointScale(project=project, creator=request.user)

        ps = data["scale_value"]
        ps = [x for x in ps if x[0]!=""]
        if len(ps) <2:
            raise ValidationError("Point Scale should have minimum 2 values.")
        """ save point values as str so it will work perfect with our code for predefined scales """
        values = map(lambda s: [str(s[0]), str(s[1])] , ps)
        point_scale.value = json.dumps(values)
        point_scale.save()
        return point_scale

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def update(self, request, organization_slug, project_slug, scale_id=None):
        data = request.data
        org, project = checkOrgProject(request, organization_slug, project_slug, True)

        point_scale = PointScale.objects.get(id=scale_id)

        ps = data["scale_value"]
        ps = [x for x in ps if x[0]!=""]
        if len(ps) <2:
            raise ValidationError("Point Scale should have minimum 2 values.")
        """ save point values as str so it will work perfect with our code for predefined scales """
        values = map(lambda s: [str(s[0]), str(s[1])] , ps)
        point_scale.value = json.dumps(values)
        point_scale.save()
        return point_scale

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def delete(self, request, organization_slug, project_slug, scale_id=None):
        org, project = checkOrgProject(request, organization_slug, project_slug, True)

        point_scale = PointScale.objects.get(id=scale_id)
        point_scale.delete()
        return "deleted"


class ProjectLeadTimeHandler(BaseHandler):
    allowed_methods = ('GET',)

    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug ):
        org, project = checkOrgProject(request, organization_slug, project_slug, True)
        try:
            stats = KanbanStat.objects.filter(project=project).order_by("-created")[0]
            return {"warning": int(stats.lead_time_65/60/24), "critical": int(stats.lead_time_85/60/24)}
        except:
            return {"warning": 0, "critical": 0}

class ProjectKanbanStatsHandler(BaseHandler):
    allowed_methods = ('GET', )

    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug ):
        org, project = checkOrgProject(request, organization_slug, project_slug, False)

        stats = project_manager.get_kanban_stats(project)
        return stats

