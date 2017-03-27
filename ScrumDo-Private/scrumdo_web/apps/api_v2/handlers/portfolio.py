from .common import *

from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from apps.projects.models import Project, Portfolio, PortfolioLevel, Iteration
from apps.projects import portfolio_managers
from apps.projects import managers as project_managers
from apps.projects.org_backlog import set_project_parents
from apps.organizations.models import Team


class PortfolioHandler(BaseHandler):
    model = Portfolio
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')
    fields = ("id",
              "root",
              "risk_types",
              "time_period",
              ("levels",
                  ("name", "item_name", "level_number", "id", "icon", "time_period", "backlog_project", "work_item_name",
                      ("projects",
                          ("id", "slug", "name", "work_item_name", "color", "icon", "active", "continuous_flow", "continuous_flow_iteration_id", "project_type",
                               ("parents", ("id", "name", "slug"))
                           )
                       )
                   )
               )
          )

    @staticmethod
    def backlog_project(obj):
        try:
            backlog = obj.projects.get(project_type = Project.PROJECT_TYPE_BACKLOG_ONLY)
        except ObjectDoesNotExist:
            portfolio = obj.portfolio
            backlog = portfolio_managers.add_portfolio_level_backlog(portfolio, obj)
        except MultipleObjectsReturned:
            backlog = obj.projects.filter(project_type = Project.PROJECT_TYPE_BACKLOG_ONLY).first()
        if backlog is not None:
            return {"id": backlog.id, "slug": backlog.slug, "name":backlog.name, "work_item_name":backlog.work_item_name}
        else:
            return None

    @staticmethod
    def risk_types(obj):
        return [ getattr(obj,"risk_type_%d" % index) for index in range(1, 8) if getattr(obj, "risk_type_%d" % index) != '']

    @staticmethod
    def project_slug(obj):
        return obj.target_project.slug

    @staticmethod
    def epic_id(obj):
        return obj.target_epic_id

    def _portfolio_for_project(self, project):
        try:
            return Portfolio.objects.get(root=project)
        except Portfolio.DoesNotExist:
            level = project.portfolio_level
            if level is None:
                return None
            return project.portfolio_level.portfolio

    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, portfolio_id=None, project_slug=None):
        org = Organization.objects.get(slug=organization_slug)

        if not org.hasReadAccess(request.user):
            raise PermissionDenied()

        if project_slug is not None:
            project = Project.objects.get(slug=project_slug)
            if not has_read_access(project, request.user):
                raise PermissionDenied("You don't have access to that Project")
            return self._portfolio_for_project(project)
        elif portfolio_id is not None:
            return Portfolio.objects.get(root__organization=org, id=portfolio_id)
        else:
            return Portfolio.objects.filter(root__organization=org)


    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def create(self, request, organization_slug):
        org = Organization.objects.get(slug=organization_slug)
        if not org.hasStaffAccess(request.user):
            raise PermissionDenied()

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def update(self, request, organization_slug, portfolio_id):
        org = Organization.objects.get(slug=organization_slug)
        if not org.hasStaffAccess(request.user):
            raise PermissionDenied()
        data = request.data

        # restrict Standard (Team Edition) to 2 level portfolio
        if org.subscription.plan.premium_plan == False and len(data['levels']) > 1:
            raise PermissionDenied()

        portfolio = Portfolio.objects.get(id=portfolio_id)
        root = portfolio.root

        risk_types = data.get("risk_types", None)
        if risk_types is not None:
            for i in range(0, len(risk_types)):
                setattr(portfolio, "risk_type_%d" % (1+i), risk_types[i])

        portfolio.time_period = data.get("time_period", portfolio.time_period)


        self._update_project_portfolio_attributes(root, org, data['root'])
        self._add_remove_levels(data['levels'], portfolio)

        for levelData in data['levels']:
            level = portfolio.levels.get(id=levelData['id'])
            self._update_level(level, levelData)

            for projectData in levelData.get('projects', []):
                if 'slug' in projectData:
                    # In this case, it's an existing project
                    project = org.projects.get(slug=projectData['slug'])
                    if project.portfolio_level != level:
                        portfolio_managers.clear_story_releases(project)
                        portfolio_managers.clear_epic_releases(project)
                        portfolio_managers.add_project_to_portfolio(level, project)
                        project.icon = level.icon
                        project.save()
                    self._update_project_portfolio_attributes(project, org, projectData)
                else:
                    # In this case, it's a brand new project that we have to create
                    project = self._create_project_in_level(org, request.user, projectData, level)
                    self._update_input_ids(projectData, data['levels'])


            # Now, there's a chance a project was removed from the level.  Let's check for those.
            desired_project_ids = {p['id'] for p in levelData.get('projects', [])}
            existing_project_ids = {p.id for p in level.projects.all() if p.project_type != Project.PROJECT_TYPE_BACKLOG_ONLY}
            to_remove = existing_project_ids - desired_project_ids
            for project_id in to_remove:
                try:
                    project = level.projects.get(id=project_id)
                    portfolio_managers.remove_project_from_portfolio_level(project, level)
                except Project.DoesNotExist:
                    # it's possible the project was moved between levels,
                    # and isn't actually here now, that's just fine
                    pass

        portfolio.save()
        
        return portfolio

    def _update_input_ids(self, projectData, levelData):
        """When input comes in and we create a project, we want all our internal id's to still make sense.  This
           method updates those project id's"""
        for level in levelData:
            for project in level['projects']:
                for parent in project['parents']:
                    if parent.get('uid', 1) == projectData.get('uid', 2):
                        parent['id'] = projectData['id']

    def _add_remove_levels(self, levelData, portfolio):
        """Adds or removes levels within the portfolio based on them existing or not within the input data"""

        # Let's remove existing ones we don't want anymore first.
        existing_ids = {l.id for l in portfolio.levels.all()}
        requested_ids = {l['id'] for l in levelData if 'id' in l}
        to_remove = existing_ids - requested_ids
        for level_id in to_remove:
            portfolio_managers.remove_portfolio_level(portfolio, portfolio.levels.get(id=level_id))

        # Now, lets find any new ones and add them in.
        # Newly created levels won't have their ID field set
        to_add = [l for l in levelData if not 'id' in l]

        for level in to_add:
            try:
                work_item_name = level['work_item_name']
            except:
                work_item_name = 'Card'

            new_level = portfolio_managers.create_portfolio_level(portfolio, level['name'], level['level_number'], level['icon'], work_item_name=work_item_name)
            
            # add backlog project to new portfolio level
            portfolio_managers.add_portfolio_level_backlog(portfolio, new_level)

            level['id'] = new_level.id

        # Finally, make sure we still have a sane numbering scheme
        portfolio_managers.renumber_portfolio_levels(portfolio)

    def _update_level(self, level, data):
        updateWorkItem = False
        level.name = data.get('name', level.name)
        icon = data.get('icon', level.icon)
        level.icon = icon if icon else 'fa-cube'
        level.time_period = data.get("time_period", level.time_period)
        # i think we do not udpate the level number here 
        # it conflicts with _add_remove_levels() -> renumber_portfolio_levels()
        #level.level_number = data.get('level_number', level.level_number)
        work_item_name = data.get("work_item_name", level.work_item_name)
        if work_item_name != level.work_item_name:
            level.work_item_name = work_item_name
            updateWorkItem = True
        level.save()
        if updateWorkItem is True:
            portfolio_managers.update_portfolio_level_backlog(level)

    def _update_project_portfolio_attributes(self, project, org, data):
        project.name = data.get('name', project.name)
        color = data.get('color', project.color)
        if isinstance(color, basestring):
            color = int(color.strip("#"), 16)
        project.color = color
        icon = data.get('icon', project.icon);
        project.icon = icon if icon != '' else 'fa-cube'
        project.work_item_name = data.get('work_item_name', project.work_item_name)

        parents = [c['id'] for c in data['parents']]
        parents = org.projects.filter(id__in=parents)
        set_project_parents(project, parents)

        project.save()

    def _create_project_in_level(self, org, user, projectData, level):
        parent_ids = [p['id'] for p in projectData['parents']]
        project = project_managers.create_project(projectData['name'],
                                                  org,
                                                  user,
                                                  False,
                                                  [],
                                                  parent_ids=parent_ids,
                                                  work_item_name=projectData['work_item_name'],
                                                  icon=projectData.get('icon','fa-cube'))
        projectData['id'] = project.id

        color = projectData.get('color', project.color)
        if isinstance(color, basestring):
            color = int(color.strip("#"), 16)
        project.color = color
        project.save()

        portfolio_managers.add_project_to_portfolio(level, project)
        return project


    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def delete(self, request, organization_slug, portfolio_id):
        org = Organization.objects.get(slug=organization_slug)
        if not org.hasStaffAccess(request.user):
            raise PermissionDenied()


class PortfolioBuildHandler(BaseHandler):
    allowed_methods = ('POST',)

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def create(self, request, organization_slug):
        org = Organization.objects.get(slug=organization_slug)
        data = request.data
        if not org.hasStaffAccess(request.user):
            raise PermissionDenied()
        existing_projects_ids = []
        # restrict Standard (Team Edition) to 2 level portfolio
        if org.subscription.plan.premium_plan == False and len(data['levels']) > 1:
            raise PermissionDenied()

        portfolio = portfolio_managers.create_portfolio(org,
                                                        data['root']['name'],
                                                        request.user,
                                                        data['root']['work_item_name'],
                                                        data['root']['icon'],
                                                        data['time_period'])

        projects = {
            'root': portfolio.root
        }

        for levelData in data['levels']:
            level = portfolio_managers.create_portfolio_level(portfolio,
                                                              levelData['name'],
                                                              levelData['level_number'],
                                                              levelData['icon'],
                                                              levelData['time_period'],
                                                              levelData['work_item_name'])
            for projectData in levelData['projects']:
                parents = [projects[c['uid']].id for c in projectData['parents']]

                if projectData['id'] and int(projectData['id']) > 0:
                    project = org.projects.get(id=projectData['id'])
                    parents = org.projects.filter(id__in=parents)
                    set_project_parents(project, parents)
                    existing_projects_ids.append(project.id)
                else:
                    project = project_managers.create_project(projectData['name'],
                                                              org,
                                                              request.user,
                                                              False,
                                                              [],
                                                              parent_ids=parents,
                                                              work_item_name=projectData['work_item_name'])
                    if "continuous_flow" in projectData and projectData["continuous_flow"] is not None and \
                        projectData["continuous_flow"] is True:
                        # set project to have continuous flow iteration
                        cont_iteration = project.iterations.filter(iteration_type=Iteration.ITERATION_WORK)[0]
                        cont_iteration.end_date = None
                        cont_iteration.name = "Continuous"
                        cont_iteration.save()
                        project.continuous_flow_iteration_id = cont_iteration.id 
                        project.save()

                project.icon = projectData['icon']
                if isinstance(projectData['color'], basestring):
                    project.color = int(projectData['color'].strip("#"), 16)
                else:
                    project.color = projectData['color']
                project.save()
                projects[projectData['uid']] = project
                portfolio_managers.add_project_to_portfolio(level, project)
        
        create_teams = data["auto_teams"]
        if create_teams is True:
            portfolio_managers.create_auto_teams(org, portfolio, request.user)

        portfolio_managers.build_portfolio_level_iterations(portfolio, existing_projects_ids = existing_projects_ids)
        portfolio_managers.autoRelatePortfolioIterations(portfolio)
        portfolio_managers.create_portfolio_global_backlogs(portfolio)

        project_managers.clearNewsItemsCache(org, None)

        return portfolio
