from piston.handler import BaseHandler
from django.conf import settings
from django.core.exceptions import PermissionDenied, ValidationError
from piston.utils import throttle
from django.core.paginator import Paginator, EmptyPage
from apps.projects.templatetags import projects_tags
from django.template import defaultfilters
from apps.projects.models import Project
from apps.organizations.models import Organization
from apps.projects.access import has_write_access, has_read_access, has_admin_access, has_staff_access,\
    get_users_cached_projects, get_users_projects_public_only, rebuild_users_projects_cache, clear_users_projects_list_cache

from django_redis import get_redis_connection

import re
import logging

logger = logging.getLogger(__name__)

ACCESS_CACHE_TIMEOUT = 120
READ_THROTTLE_REQUESTS = 150
WRITE_THROTTLE_REQUESTS = 50
THROTTLE_TIME = 5


def paginate(queryset, request, customHandler=None):
    page = int(request.GET.get("page", "1"))
    perPage = int(request.GET.get("perPage", "100"))
    try:
        p = Paginator(queryset, perPage)
        logger.debug("Custom handler: %s" % customHandler)
        if customHandler:
            for obj in p.page(page).object_list:
                setattr(obj, "apiMapper", customHandler)

        return { 'current_page':page, 'max_page':p.num_pages, 'count':p.count, 'items':p.page(page).object_list}
    except EmptyPage:
        return []

def linkStories(input, project):
    """
        Links stories in the format "Story #5" or "Card #5" to a permalink for that story.
        Story #4
        will become...
        <a href='/projects/story_permalink/390482'>Story #4</a>
        It will try to not re-create stupid nested links by excluding anything with </a> after it.
    """
    def replaceLink(value):
        try:
            if value.group(3) is not None:
                # Most likely aleady wrapped.
                return value.group(0)
            local_id = value.group(2)
            story = project.stories.get(local_id=int(local_id) )
            return "<a href=\"%s/projects/story_permalink/%d\">%s</a>" % (settings.SSL_BASE_URL, story.id, value.group(0))
        except:
            return value.group(0)
    try:
        if input is None or input == '':
            return ''
        return re.sub(r'(?i)(story|card) #([0-9]+)(</a>)?', replaceLink, input)
    except:
        return input

def linkStoriesVer2(input, project):
    """
        Links stories in the format "Story XX-5" or "Card XX-5" to a permalink for that story.
        Story XX-4
        will become...
        <a href='/projects/story_permalink/390482'>Story XX-4</a>
        It will try to not re-create stupid nested links by excluding anything with </a> after it.
        XX = Project Prefix
    """
    P = (project,)
    def replaceLinkVer2(value):
        try:
            if value.group(4) is not None:
                # Most likely aleady wrapped.
                return value.group(0)
            local_id = value.group(3)
            prefix = value.group(2)
            # not able to access project variable here, got working with this
            project = P[0]
            if prefix == project.prefix:
                story = project.stories.get(local_id=int(local_id))
            else:
                try:
                    project = Project.objects.get(prefix=prefix.upper(), organization = project.organization)
                    story = project.stories.get(local_id=int(local_id))
                except:
                    return value.group(0)
            return "<a href=\"%s/projects/story_permalink/%d\">%s</a>" % (settings.SSL_BASE_URL, story.id, value.group(0))
        except:
            return value.group(0)
    try:
        if input is None or input == '':
            return ''
        v = re.sub(r'(?i)(story|card) ([A-Z,0-9]{2})-([0-9]+)(</a>)?', replaceLinkVer2, input)
        return linkStories(v, project)
    except:
        return input


def htmlify(input, project):
    if input is None:
        return None
    res = projects_tags.urlify2(projects_tags.markdown_save(defaultfilters.force_escape(input)))
    if project is not None:
        return projects_tags.link_stories(res, project)
    return res


def _hasOrgReadAccess(organization, user):
    redis = get_redis_connection('default')
    cache_key = "org-read-{organization.id}-{user.id}".format(organization=organization, user=user)
    cached = redis.get(cache_key)
    if cached:
        return cached == 'True'
    access = organization.hasReadAccess(user)
    if access:
        redis.setex(cache_key, ACCESS_CACHE_TIMEOUT, access)
    return access


def checkOrgProject(request, organization_slug, project_slug, check_write_access=False):
    """ Checks that
            1. The organization and project exists.
            2. The project is part of the organization
            3. The user has at least read access to the org and project.
            4. (optionally) the user has write access
    """

    org = Organization.objects.get(slug=organization_slug)

    if not _hasOrgReadAccess(org, request.user):
        raise PermissionDenied("You don't have access to that Organization")

    project = Project.objects.get(slug=project_slug)

    if check_write_access:
        if not has_write_access(project, request.user):
            raise PermissionDenied("You don't have access to that Project")
    else:
        if project.project_type == Project.PROJECT_TYPE_PORTFOLIO:
            pass  # Everyone who can read the org, can read this project.
        else:
            if not has_read_access(project, request.user):
                raise PermissionDenied("You don't have access to that Project")

    if project.organization_id != org.id:
        raise ValidationError("Organization and project don't match")

    return org, project


