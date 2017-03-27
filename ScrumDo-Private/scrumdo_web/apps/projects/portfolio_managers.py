from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from models import Portfolio, PortfolioLevel, Project, ProgramIncrementSchedule, Iteration, ProgramIncrement
import managers
from apps.projects import org_backlog
from apps.projects import signals
from apps.organizations.models import Team
import apps.projects.tasks as projects_tasks
import util as util
import datetime


# def get_assignemnts(project, portfolio, story)

def is_project_in_portfolio(project, portfolio):
    return (project.portfolio_level and project.portfolio_level.portfolio == portfolio) or (portfolio.root == project)

def create_portfolio(organization, name, creator, work_item_name, icon, time_period='Portfolio Increment'):
    root = managers.create_project(name, organization, creator, False, [], project_type = Project.PROJECT_TYPE_PORTFOLIO ,work_item_name=work_item_name)
    root.project_type = Project.PROJECT_TYPE_PORTFOLIO
    root.icon = icon
    root.save()
    portfolio = Portfolio(root=root, organization=organization, time_period=time_period)
    portfolio.save()
    return portfolio


def renumber_portfolio_levels(portfolio):
    c = 1
    for level in portfolio.levels.all().order_by('level_number'):
        if level.level_number != c:
            level.level_number = c
            level.save()
        c+=1

# not neeed any more 
# can be removed
# def delete_increment_schedule(schedule, request):
#     for iteration in schedule.iterations.all():
#         if iteration.stories.count() == 0:
#             # We can delete empty iterations
#             managers.delete_iteration(iteration.project, iteration, request)
#         else:
#             # But if they have cards, we're just going to remove them from the increment.
#             iteration.program_increment_schedule = None
#             iteration.save()

#     schedule.delete()


def create_increment_schedule(project, increment, start_date, default_name, request):
    schedule = ProgramIncrementSchedule(increment=increment,
                                        start_date=start_date,
                                        default_name=default_name)
    schedule.save()

    for child in project.children.all():
        iteration = Iteration(project=child,
                              name=default_name,
                              start_date=start_date,
                              end_date=end_date,
                              program_increment_schedule=schedule,
                              iteration_type=Iteration.ITERATION_WORK)

        iteration.full_clean()
        iteration.save()
        signals.iteration_created.send(sender=request, iteration=iteration, user=request.user)

    return schedule


def update_increment_schedule(schedule, name, start_date, end_date):
    for iteration in schedule.iterations.all():
        if iteration.name == schedule.default_name:  # Only update iteration names if they haven't been modified
            iteration.name = name
        iteration.start_date = start_date
        iteration.end_date = end_date
        iteration.save()

    schedule.default_name = name
    schedule.start_date = start_date
    schedule.save()
    return schedule


def remove_portfolio_level(portfolio, level, deleteProjects = False):
    # first remove level Backlog Project
    remove_portfolio_level_backlog(level)
    # Need to remove any projects in the level from the level first.
    for project in level.projects.all():
        remove_project_from_portfolio_level(project, level)
        if deleteProjects is True:
            managers.delete_project(project)

    if level.level_number == 1:
        # Special case, we are removing the first level, so there
        # might be a new first-level and we should set
        # it's parents to the root-project of the portfolio
        pass

    # Finally, actually remove the level
    level.delete()


def create_portfolio_level(portfolio, name, level_number, icon, time_period='Iteration', work_item_name='Card'):
    level = PortfolioLevel(portfolio=portfolio, name=name, level_number=level_number, icon=icon, time_period=time_period, work_item_name=work_item_name)
    level.save()
    return level

def create_portfolio_global_backlogs(portfolio):
    for level in portfolio.levels.all():
        add_portfolio_level_backlog(portfolio, level)


def add_portfolio_level_backlog(portfolio, level):
    org = portfolio.organization
    backlog = None
    try:
        backlog = level.projects.get(project_type = Project.PROJECT_TYPE_BACKLOG_ONLY)
    except MultipleObjectsReturned:
        return backlog
    except ObjectDoesNotExist:
        work_item_name = level.work_item_name
        user = portfolio.root.creator
        backlog = managers.create_project(work_item_name,
                                            org,
                                            user,
                                            False,
                                            [],
                                            project_type = Project.PROJECT_TYPE_BACKLOG_ONLY,
                                            work_item_name = work_item_name,
                                            icon='fa-cube')
        if backlog is not None:
            add_project_to_portfolio(level, backlog)

    return backlog

def update_portfolio_level_backlog(level):
    try:
        backlog = level.projects.get(project_type = Project.PROJECT_TYPE_BACKLOG_ONLY)
        backlog.work_item_name = level.work_item_name
        backlog.save()
    except ObjectDoesNotExist:
        pass    

def remove_portfolio_level_backlog(level):
    try:
        backlog = level.projects.get(project_type = Project.PROJECT_TYPE_BACKLOG_ONLY)
        remove_project_from_portfolio_level(backlog, level)
        managers.delete_project(backlog)
    except ObjectDoesNotExist:
        pass

def add_project_to_portfolio(portfolioLevel, project, userAction = True):
    remove_project_from_portfolio(project, userAction)
    portfolioLevel.projects.add(project)
    if userAction is True:
        # rebuild owner project list cache
        projects_tasks.queueRebuildUserProjectListCache(project.organization, project.creator)
        # also rebuild teams project list cache
        rebuild_portfolio_nonroot_teams_cache(project)

def delete_portfolio(rootProject):
    # try if this is a rootProject in a portfolio
    try:
        portfolio = Portfolio.objects.get(root=rootProject)
        for level in portfolio.levels.all():
            remove_portfolio_level(portfolio, level, deleteProjects = True)
        portfolio.delete()
    except ObjectDoesNotExist:
        # got a org release instead of portfolio
        for child in rootProject.children.all():
            clear_story_releases(child, rootProject)
            clear_epic_releases(child, rootProject)
            org_backlog.remove_project_parent(child, rootProject)
        organization = rootProject.organization
        # set org planning mode to unset
        organization.planning_mode = "unset"
        organization.save()

def archive_portfolio_projects(rootProject):
    # try if this is a rootProject in a portfolio
    try:
        portfolio = Portfolio.objects.get(root=rootProject)
        for level in portfolio.levels.all():
            for project in level.projects.all():
                project.active = False
                project.save()
    except ObjectDoesNotExist:
        # got a org release instead of portfolio
        pass

def activate_portfolio_projects(rootProject):
    # try if this is a rootProject in a portfolio
    try:
        portfolio = Portfolio.objects.get(root=rootProject)
        for level in portfolio.levels.all():
            for project in level.projects.all():
                project.active = True
                project.save()
    except ObjectDoesNotExist:
        # got a org release instead of portfolio
        pass

def remove_project_from_portfolio(project, userAction = True):
    if project is None:
        return
    if project.portfolio_level is None:
        return
    remove_project_from_portfolio_level(project, project.portfolio_level, userAction)


def clear_story_releases(project, parent=None):
    q = project.stories.filter(release__isnull=False)
    if parent is not None:
        q = q.filter(release__project=parent)
    for story in q:
        # So, we want to remove any references to the portfolio within cards
        story.release = None
        story.save()


def clear_epic_releases(project, parent=None):
    q = project.epics.filter(release__isnull=False)
    if parent is not None:
        q = q.filter(release__project=parent)

    for epic in q:
        # Also, epics
        epic.release = None
        epic.save()


def remove_project_from_portfolio_level(project, level, userAction = True):
    clear_story_releases(project)
    clear_epic_releases(project)

    for parent in project.parents.all():
        # Need to remove it's parents since they wouldn't be valid anymore
        org_backlog.remove_project_parent(project, parent)

    for child in project.children.all():
        # Also, if it has child projects, they should no longer point to the current project
        clear_story_releases(child, project)
        clear_epic_releases(child, project)
        org_backlog.remove_project_parent(child, project)
    
    # clear all Increment Schedule related to parent projects
    clear_project_increment_schedule(project)

    project.portfolio_level = None
    project.save()

    if userAction is True:
        # rebuild owner project list cache
        projects_tasks.queueRebuildUserProjectListCache(project.organization, project.creator)
        # also rebuild teams project list cache
        rebuild_portfolio_projects_teams_cache(level.portfolio.root)
        # rebuild all team cache having this in list
        for team in project.organization.teams.all():
            if project in team.projects.all():
                managers.rebuild_project_teams_cache_fn(project.organization, team)

def clear_project_increment_schedule(project):
    for iteration in project.iterations.filter(program_increment_schedule__isnull = False):
        iteration.program_increment_schedule.clear()

def move_portfolio_to_org(project, organization):
    managers.remove_project_from_teams(project)
    # try if this is a rootProject in a portfolio
    try:
        portfolio = Portfolio.objects.get(root=project)
        for level in portfolio.levels.all():
            for p in level.projects.all():
                managers.remove_project_from_teams(p)
                p.organization = organization
                if "duplicatePrefix" in dir(util):
                    if not util.duplicatePrefix(p, organization):
                        p.save()
                    else:
                        p.prefix = util.generateProjectPrefix(p)
                        p.save()
                else:
                    p.save()
        if "duplicatePrefix" in dir(util):
            if util.duplicatePrefix(project, organization):
                project.prefix = util.generateProjectPrefix(project)
            
    except ObjectDoesNotExist:
        # got a org release instead of portfolio root to be moved 
        for child in project.children.all():
            clear_story_releases(child, project)
            clear_epic_releases(child, project)
            org_backlog.remove_project_parent(child, project)
        # set org planning mode to unset
        org = project.organization
        org.planning_mode = "unset"
        org.save()
    project.organization = organization
    #finally save the project
    project.save()

def rebuild_portfolio_projects_teams_cache(rootProject):
    # try if this is a rootProject in a portfolio
    try:
        portfolio = Portfolio.objects.get(root=rootProject)
        all_teams = []
        all_team_keys = {}
        for level in portfolio.levels.all():
            projects = level.projects.all()
            teams = rootProject.organization.teams.filter(projects__in=projects).distinct()
            all_teams.extend(teams)
        for team in all_teams:
            if team.id not in all_team_keys:
                all_team_keys[team.id] = team
                managers.rebuild_project_teams_cache_fn(rootProject.organization, team)
    except ObjectDoesNotExist:
        # got a org release instead of portfolio root to be moved 
        teams = rootProject.organization.teams.filter(projects=rootProject).distinct()
        for team in teams:
            managers.rebuild_project_teams_cache_fn(rootProject.organization, team)

def rebuild_portfolio_nonroot_teams_cache(project):
    if project.portfolio_level is None:
        return
    rootProject = project.portfolio_level.portfolio.root
    rebuild_portfolio_projects_teams_cache(rootProject)

def create_auto_teams(organization, portfolio, owner):
    for level in portfolio.levels.all():
        projects = level.projects.all()
        level_team = Team(organization=organization, name='%s %s Members' % (portfolio.root.name, level.name,), access_type='write')
        level_team.save()
        for project in projects:
            project_team = Team(organization=organization, name='%s Members' % (project.name,), access_type='write')
            project_team.save()
            project_team.projects.add(project)
            project_manager_team = Team(organization=organization, name='%s Managers' % (project.name,), access_type='admin')
            project_manager_team.save()
            project_manager_team.projects.add(project)
            project_manager_team.members.add(owner)

            level_team.projects.add(project)
    return

def autoRelatePortfolioIterations(portfolio):
    """
    We will auto related all level Iterations for a Portfolio while creating it
    i.e Program Level Iterations would have parent as Root level
        Team Level Iteration would have parent as Program level 
    """
    root = portfolio.root

    for level in portfolio.levels.all():
        projects = level.projects.all()
        for project in projects:
            try:
                parents = project.parents.all()
                for parent in parents:
                    increment = parent.iterations.filter(iteration_type=Iteration.ITERATION_WORK, hidden = False)[0]
                    iterations =  project.iterations.filter(iteration_type=Iteration.ITERATION_WORK, hidden = False)
                    for iteration in iterations:
                        _relate_iteration_increment(project, increment, iteration)
            except KeyError:
                # no parent found
                pass


def _relate_iteration_increment(project, parent_iteration, iteration):
        """
        will set the iteration increment to parent increment
        will select the schedule based on start data, if one exist already
        select that otherwise create new one with start date
        also create increment record if doesn't exist related to parent Iteration
        """
        try:
            increment, created = ProgramIncrement.objects.get_or_create(iteration_id=parent_iteration.id)
            try:
                schedule = ProgramIncrementSchedule.objects.get(increment=increment, start_date = project.created)
            except MultipleObjectsReturned:
                schedule = ProgramIncrementSchedule.objects.filter(increment=increment, start_date = project.created).first()
            except ObjectDoesNotExist:
                schedule = ProgramIncrementSchedule(increment=increment,
                                                    start_date = project.created,
                                                    default_name=iteration.name)
                schedule.save()

            iteration.program_increment_schedule.add(schedule)
        except KeyError:
            pass

def build_portfolio_level_iterations(portfolio, existing_projects_ids = []):
    """
    will create Iterations in each level projects
    4 level Portfolio :
        Solution Increment 1
            Program Increment 1.1
                Sprint 1.1.1, Sprint 1.1.2, Sprint 1.1.3 and Sprint 1.1.4 and Sprint 1.1.5
    3 level Portfolio
        Program Increment 1
            Sprint 1.1, Sprint 1.2, Sprint 1.3 and Sprint 1.4 and Sprint 1.5
    2 level
        Sprint 1 Sprint 2, Sprint 3 and Sprint 4 and Sprint 5
    """
    root = portfolio.root
    levels = portfolio.levels.all().order_by("level_number")
    if levels.count() > 3:
        # no need to automate for bigger then Four Level SAFe
        return
    #first re number levels in case they are not
    renumber_portfolio_levels(portfolio)

    for level in levels:
        level_number = level.level_number
        index = levels.count() - level_number

        if index == 0:
            # Team level projects
            for project in level.projects.filter(project_type = Project.PROJECT_TYPE_KANBAN, continuous_flow_iteration__isnull = True)\
                                        .exclude(id__in=existing_projects_ids):
                initial_extra = ''
                if levels.count() ==3:
                    initial_extra = '1.1.'
                if levels.count() ==2:
                    initial_extra = '1.'

                iteration_counts = 1
                iteration_counts = _update_level_project_iterations(project, 
                                                                    initial=level.time_period, 
                                                                    initial_extra=initial_extra,
                                                                    duration=14, 
                                                                    counter = 1)
                while iteration_counts <= 5:
                    days = (iteration_counts-1)*15
                    start_date = datetime.date.today() + datetime.timedelta(days=days)
                    iteration_counts = _create_level_project_iterations(project, 
                                                                        initial=level.time_period, 
                                                                        initial_extra=initial_extra,
                                                                        duration=14, 
                                                                        start_date = start_date,
                                                                        counter = iteration_counts)

        elif index == 1:
            # Program level projects
            for project in level.projects.filter(project_type = Project.PROJECT_TYPE_KANBAN, continuous_flow_iteration__isnull = True)\
                                        .exclude(id__in=existing_projects_ids):
                initial_extra = ''
                if levels.count() ==3:
                    initial_extra = '1.'

                _update_level_project_iterations(project, 
                                                initial=level.time_period, 
                                                initial_extra=initial_extra,
                                                duration=70, 
                                                counter = 1)
            
        elif index == 2:
            # Value Stream level projects
            for project in level.projects.filter(project_type = Project.PROJECT_TYPE_KANBAN, continuous_flow_iteration__isnull = True)\
                                        .exclude(id__in=existing_projects_ids):
                _update_level_project_iterations(project, 
                                                initial=level.time_period, 
                                                duration=140, 
                                                counter = 1)


def _create_level_project_iterations(project, initial="Iteration", initial_extra="", start_date = None, duration = 14, counter = 1):
    name = "%s %s%s" % (initial, initial_extra, counter)
    if start_date is None:
        start_date=datetime.date.today()

    end_date=start_date + datetime.timedelta(days=duration)

    iteration = Iteration(name=name,
                detail='',
                project=project,
                start_date=start_date,
                end_date=end_date,
                iteration_type=Iteration.ITERATION_WORK)

    iteration.save()

    counter += 1
    return counter

def _update_level_project_iterations(project, initial="Iteration", initial_extra="", start_date = None, duration = 14, counter = 1):
    iteration = project.iterations.filter(iteration_type=Iteration.ITERATION_WORK)[0]
    name = "%s %s%s" % (initial, initial_extra, counter)
    if start_date is None:
        start_date=datetime.date.today()
    end_date=start_date + datetime.timedelta(days=duration)

    iteration.name = name
    iteration.start_date = start_date
    iteration.end_date = end_date
    iteration.save()
    counter += 1
    return counter
