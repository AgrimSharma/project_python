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


from apps.projects.models import Project
from apps.organizations.models import Organization, Team

from django.core.exceptions import PermissionDenied

from django.core.cache import cache
from django.db.models import Q

import logging

logger = logging.getLogger(__name__)

CACHE_PERMISSION_SECONDS = 300
LONG_CACHE_PERMISSION_SECONDS = 43200 # one day long

def team_admin_access_or_403(team, user, ignore_active=False):
    for project in team.projects.all():
        if not has_admin_access(project, user, ignore_active=ignore_active):
            raise PermissionDenied("You don't have admin access to that team.")

def admin_access_or_403(project, user, ignore_active=False):
    if not has_admin_access(project, user, ignore_active=ignore_active):
        raise PermissionDenied("You don't have admin access to that project.")


def read_access_or_403(project, user):
    if not has_read_access(project, user):
        raise PermissionDenied("You don't have read access to that project")


def write_access_or_403(project, user):
    if not has_write_access(project, user):
        raise PermissionDenied("You don't have write access to that project")


def has_staff_access(organization, user):
    try:
        # if user.is_staff:
        #     return True
        key = cache_key(organization, user, "staff")
        cached_value = cache.get(key)
        if not cached_value:
            access = organization.teams.filter(access_type="staff", members=user).count() > 0
            if access:
                cache.set(key, access, CACHE_PERMISSION_SECONDS)
            return access
        else:
            return True
    except:
        return False


def has_admin_access(project, user, ignore_active=False):
    try:
        if not ignore_active:
            if not project.active:
                return False
        key = cache_key(project, user, "admin")
        cached_value = cache.get(key)
        if not cached_value:
            access = real_has_admin_access(project,user)
            if access:
                cache.set(key, access, CACHE_PERMISSION_SECONDS)
            return access
        else:
            return True  # memcache stores True/False as 1/0, we want to actually return a boolean here.
    except:
        return False


def real_has_admin_access(project, user):
    if project.personal:
        return project.creator_id == user.id
    if user.is_staff:
        return True
    if has_staff_access(project.organization, user):
        return True    
    if Organization.objects.filter(teams__members=user, teams__access_type="admin", teams__projects=project).count() > 0:
        return True

    if project.portfolio_level is not None:
        return portfolio_has_admin_access(project, user)
    else:
        return False


def has_write_access( project, user, ignore_active=False):
    try:
        if (not project.active) and (not ignore_active):
            return False
        key = cache_key(project, user, "write")
        cached_value = cache.get(key)
        if not cached_value:
            access = real_has_write_access(project, user, ignore_active=ignore_active)
            if access:
                cache.set(key, access, CACHE_PERMISSION_SECONDS)
            return access
        else:
            return True  # memcache stores True/False as 1/0, we want to actually return a boolean here.
    except:
        return False


def real_has_write_access( project, user, ignore_active=False ):

    if project.personal:
        return project.creator_id == user.id
    if user.is_staff:
        return True
    if has_admin_access(project, user, ignore_active=ignore_active):
        return True

    if Organization.objects.filter(teams__members=user, teams__access_type="write", teams__projects=project).count() > 0:
        return True

    if project.portfolio_level is not None and project.project_type == Project.PROJECT_TYPE_BACKLOG_ONLY:
        # A portfolio level backlog project can be write by anyone
        # having write access to atleast one project in level.
        return portfolio_level_has_write_access(project, user)

    if project.portfolio_level is not None and project.project_type != Project.PROJECT_TYPE_PORTFOLIO:
        return portfolio_has_write_access(project, user)
    else:
        return False


def has_read_access(project, user):
    try:
        if project.personal:
            return project.creator_id == user.id

        if user.is_staff:
            return True

        key = cache_key(project, user, "read")
        cached_value = cache.get(key)
        if not cached_value:
            access = real_has_read_access(project, user)
            if access:
                cache.set(key, access, CACHE_PERMISSION_SECONDS)
            return access
        else:
            return True  # memcache stores True/False as 1/0, we want to actually return a boolean here.
    except:
        return False


def real_has_read_access(project, user):
    if project.personal:
        return project.creator_id == user.id                
    if has_admin_access(project, user, ignore_active=True):
        return True
    if has_write_access(project, user):
        return True

    if project.project_type == Project.PROJECT_TYPE_PORTFOLIO:
        # A portfolio project can be read by anyone in the organization.
        return project.organization.hasReadAccess(user)

    if project.project_type == Project.PROJECT_TYPE_BACKLOG_ONLY:
        # A portfolio level backlog project can be read by anyone
        # having read access to atleast one project in level.
        return portfolio_level_has_read_access(project, user)

    if Organization.objects.filter(teams__members=user, teams__projects=project).count() > 0:
        return True

    if project.portfolio_level is not None:
        return portfolio_has_read_access(project, user)
    else:
        return False


def cache_key(project, user, acc_type):
    return "acc_%s_%s_%d_%d" % (acc_type, project.slug, project.id, user.id)

    
def getProjectsForUser(user, organization=None):
    """ This gets all a user's projects, including ones they have access to via teams. """
    rv = []
    for project in organization.projects.all():
        if has_read_access(project, user):
            rv.append(project)
    return rv


def getAssignedStories(user, organization):
    projects = getProjectsForUser(user, organization=organization)
    assigned_stories = []
    for project in projects:
        if project.active:
            project_stories = []
            iterations = project.get_current_iterations(organization=organization)
            for iteration in iterations:
                project_stories = project_stories + list(iteration.stories.filter(assignee=user).exclude(status=10).select_related())
                project_stories = project_stories + list(iteration.stories.filter(tasks__assignee=user).exclude(status=10).select_related())
            if len(project_stories) > 0:
                assigned_stories = assigned_stories + [(project, list(set(project_stories)))]
    return assigned_stories

def child_has_read_access(parent, user):
    for child in parent.children.all():
        if has_read_access(child, user):
            return True
        if child_has_read_access(child, user):
            return True
    return False

def portfolio_has_read_access(project, user):
    projects = get_portfolio_projects(project) 
    return  Organization.objects.filter(teams__members=user, teams__projects__in=projects).count() > 0

def portfolio_has_write_access(project, user):
    parent_projects = get_portfolio_parents(project, [])
    return  Organization.objects.filter(teams__members=user, teams__access_type="write", teams__projects__in=parent_projects).count() > 0

def portfolio_has_admin_access(project, user):
    parent_projects = get_portfolio_parents(project, [])
    return  Organization.objects.filter(teams__members=user, teams__access_type="admin", teams__projects__in=parent_projects).count() > 0

def portfolio_level_has_read_access(project, user):
    if project.portfolio_level is None:
        return False
    access = False
    level_projects = _get_portfolio_project_level_projects(project)
    for project in level_projects:
        if has_read_access(project, user):
            access = True
            break
    return access

def portfolio_level_has_write_access(project, user):
    if project.portfolio_level is None:
        return False
    level_projects = _get_portfolio_project_level_projects(project)
    access = False
    for project in level_projects:
        if has_write_access(project, user):
            access = True
            break
    return access

def _get_portfolio_project_level_projects(project):
    portfolio = project.portfolio_level.portfolio
    level = project.portfolio_level
    level_projects = level.projects.filter(project_type = Project.PROJECT_TYPE_KANBAN)
    return level_projects

def get_portfolio_parents(project, parents):
    for parent in project.parents.all():
        if parent.project_type != Project.PROJECT_TYPE_PORTFOLIO:
            parents.append(parent)
        if parent.parents.all():
            get_portfolio_parents(parent, parents)
        else:
            pass
    return parents

def get_portfolio_children(project, children):
    for child in project.children.all():
        children.append(child)
        if child.children.all():
            get_portfolio_children(child, children)
        else:
            pass
    return children

def get_portfolio_projects(project):
    try:
        parents = get_portfolio_parents(project, [])
        children = get_portfolio_children(project, [])
        return parents+children
    except:
        return []

def parent_has_write_access(child, user):
    for parent in child.parents.all():
        if has_write_access(parent, user):
            return True
        if parent_has_write_access(parent, user):
            return True
    return False

def parent_has_admin_access(child, user):
    for parent in child.parents.all():
        if has_admin_access(parent, user):
            return True
        if parent_has_admin_access(parent, user):
            return True
    return False

def project_list_cache_key(acc_type, user, org):
    return "project_list_%s_%d_%d" % (acc_type, user.id, org.id)

def clear_users_projects_list_cache(org, user, acc_type="read"):
    projects_cache_key = project_list_cache_key(acc_type, user, org)
    staff_key = cache_key(org, user, "staff")
    cache.delete(staff_key)
    projects = cache.get(projects_cache_key)
    if projects is not None:
        for project in projects:
            read_key = cache_key(project, user, acc_type)
            admin_key = cache_key(project, user, "admin")
            write_key = cache_key(project, user, "write")
            cache.delete(read_key)
            cache.delete(write_key)
            cache.delete(admin_key)
    cache.delete(projects_cache_key)

def rebuild_users_projects_cache(org, user):
    rv = []
    #clear projects cache first, so we always get right access
    clear_users_projects_list_cache(org, user, "read")
    projects =  org.projects.filter(Q(project_type=Project.PROJECT_TYPE_KANBAN)\
                | Q(project_type=Project.PROJECT_TYPE_BACKLOG_ONLY)\
                | Q(project_type=Project.PROJECT_TYPE_PORTFOLIO), active=True)\
                .select_related("organization","portfolio_level")\
                .prefetch_related("tags", "labels", "teams", "teams__members", "parents", "children").distinct()\
                .order_by("project_type")
    for project in projects:
        if has_read_access(project, user):
            rv.append(project)

    projects_cache_key = project_list_cache_key("read", user, org)
    cache.set(projects_cache_key, rv, LONG_CACHE_PERMISSION_SECONDS)
    return rv

def get_users_cached_projects(org, user):
    projects_cache_key = project_list_cache_key("read", user, org)
    cached_value = cache.get(projects_cache_key)
    if not cached_value:
        projects = rebuild_users_projects_cache(org, user)
        cache.set(projects_cache_key, projects, LONG_CACHE_PERMISSION_SECONDS)
        return projects
    else:
        return cached_value

def get_users_projects_public_only(org, user):
    all_projects = get_users_cached_projects(org, user)
    rv = []
    for project in all_projects:
        if not project.personal:
            rv.append(project)
    return rv

def has_project_in_cache_list(project, user):
    projects_cache_key = project_list_cache_key("read", user, project.organization)
    cached_projects = cache.get(projects_cache_key)
    if not cached_projects:
        return False
    else:
        return project in cached_projects