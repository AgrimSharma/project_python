from django.db.models import Q
from django.shortcuts import render_to_response, get_object_or_404
from django.shortcuts import render_to_response, redirect
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.template import RequestContext
from haystack.query import SearchQuerySet
from apps.projects.access import has_read_access
from django.contrib.auth.decorators import login_required
from util import organizationOrNone
from models import *
from access import *
from rollbardecorator import logdeprecated
import sys, traceback
import datetime
import pyparsing
import re

import logging

logger = logging.getLogger(__name__)



def _getProjectsUserCanSee(user, organization):
    r = []
    for project in organization.projects.all():
        if has_read_access(project, user):
            r.append(project)
    return r
            

def _getMembersUserCanSee(user, organization):
    isStaff = organization.hasStaffAccess(user)
    r = []
    for team in organization.teams.all():
        members = team.members.all()
        if isStaff or user in members:
            r += members
    return r

    
@login_required
def search_organization(request, organization_slug):    
    organization = get_object_or_404( Organization, slug=organization_slug )

    # read_access_or_403(project, request.user )
    search_terms = request.GET.get("q","")

    # We used to do the search all server side, now we rely on a client side app to call the api and do it.
    # return do_search(request, organization, None, template_name="", check_access=True)
    return render_to_response("organizations/organization_search.html", 
                            {
                              "search_terms":search_terms,
                              "organization":organization
                            },
                            context_instance=RequestContext(request))
    

@login_required
def search_project(request, project_slug):
    project = get_object_or_404( Project, slug=project_slug )
    organization = organizationOrNone(project)
    read_access_or_403(project, request.user )
    search_terms = request.GET.get("q","")
    url = '{}#/search?q={}'.format(reverse('project_app', kwargs={'project_slug':project_slug}), search_terms)
    return redirect(url)


def do_search(request, organization, project = None, template_name="projects/search_results.html", check_access=False):
    query_string = request.GET.get("q")
    q = parseQuery(query_string)
    search_results = performSearch(q, organization, project)

    if check_access and not organization.hasStaffAccess(request.user):
        search_results = search_results.load_all()
        search_results = [story for story in search_results if has_read_access(story.object.project, request.user)]
        search_count = len(search_results)
    else:
        search_count = search_results.count()
    logger.debug('Search Results: %' %search_results)
    return render_to_response(template_name, 
                            {
                              "project":project,
                              "search_terms":query_string,
                              "organization":organization,
                              "search_results":search_results,
                              "query": q,
                              "search_count": search_count
                            },
                            context_instance=RequestContext(request))


def to_date(s):
    formats = ["%Y-%m-%d","%m/%d/%Y","%d/%m/%Y"]
    for f in formats:
        try:
            print "Trying %s %s" % (s,f)
            return datetime.datetime.strptime(s, f).date()
        except:
            pass
    return None
    
def parseQuery(query_string):
    query_string = query_string.lower()
    query_terms = ("status_int",
                   "numeric_points",
                   "order",
                   "number",
                   "epic",
                   "card_type",
                   "cell",
                   "createdafter",
                   "labels",
                   "createdbefore",
                   "updatedafter",
                   "updatedbefore",
                   "movedafter",
                   "movedbefore",
                   "category",
                   "contains",
                   "release",
                   "release_prefix",
                   "tag",
                   "epics",
                   "assignee",
                   "creator",
                   "prefix")
    equivalent_criteria = {"points": "numeric_points",
                           "assigned": "assignee",
                           "after": "updatedafter",
                           "before": "updatedbefore",
                           "label": "labels",
                           "cat": "category",
                           "release": "release",
                           "#": "number"}

    query = {'order': [], 'phrases': []}

    logger.debug("Parsing query %s" % query_string)

    for term in query_terms:
        query[term] = []
    
    try:
        params = pyparsing.CharsNotIn(":,").setResultsName("criteria") + pyparsing.Suppress(":") + pyparsing.Suppress(pyparsing.Optional(pyparsing.White())) + pyparsing.CharsNotIn(":,").setResultsName("argument")
        quoted_words = pyparsing.quotedString.setResultsName("text")
        words = pyparsing.CharsNotIn(":,").setResultsName("text")
        other = pyparsing.restOfLine.setResultsName("text")
        search_term = pyparsing.Group(params | quoted_words | words)
        parser = pyparsing.StringStart() + pyparsing.ZeroOrMore( search_term + pyparsing.Suppress(pyparsing.Optional(",")) ) + pyparsing.StringEnd()
        result = parser.parseString(query_string)    
        for token in result:
            criteria = token.criteria.lower()
            if criteria in equivalent_criteria:
                criteria = equivalent_criteria[criteria]
            if criteria in query_terms:
                logger.debug("Searching [%s]=[%s]" % (criteria, token.argument))
                if criteria == 'epic' or criteria == 'epics':
                    if token.argument == "-1":
                        query[criteria].append('epic_number_None')
                    else:
                        query[criteria].append('epic_number_%s' % token.argument)
                else:
                    query[criteria].append(token.argument)
            else:
                logger.debug("Searching phrase %s" % " ".join(token))
                number_search = re.search("^\s*#([0-9]+)\s*$"," ".join(token) )
                number_prefix_search = re.search("^\s*([A-Z,a-z,0-9]{2})-([0-9]+)\s*$"," ".join(token) )
                if number_search != None:
                    logger.debug("Searching number %s" % number_search.group(1))
                    # Special case, if a user types #40 they mean story number 40
                    story_number = number_search.group(1)
                    query['number'].append(story_number)
                elif number_prefix_search != None:
                    logger.debug("Searching prefix %s" % number_prefix_search.group(1))
                    logger.debug("Searching number %s" % number_prefix_search.group(2))
                    story_number = number_prefix_search.group(2)
                    query['number'].append(story_number)
                    query['prefix'].append(number_prefix_search.group(1).upper())
                else:
                    query["phrases"].append(" ".join(token))
            
    except:
        traceback.print_exc(file=sys.stdout)    
        logger.warn("Could not parse query")
        query["phrases"] = [query_string]
    return query


def performSearch(query_object, organization, project, iterations=None, onlyStories=False):
    query = SearchQuerySet()
    if onlyStories:
        query = query.models(Story)

    if iterations:
        iterationIds = [i.id for i in iterations]
        if len(iterationIds) > 0:
            query = query.filter(iteration_id__in=iterationIds)

    elif project:
        query = query.filter(project_id=project.id)
    else:
        query = query.filter(organization_id=organization.id)

    for phrase in query_object["phrases"]:
        query = query.filter(text=phrase)
    
    if len(query_object["prefix"]) > 0:
        query = query.filter(project_prefix__in=query_object['prefix'])

    if len(query_object["release"]) > 0:
        query = query.filter(release_number__in=query_object['release'])

    if len(query_object["release_prefix"]) > 0:
        query = query.filter(release_prefix__in=query_object['release_prefix'])

    if len(query_object["status_int"]) > 0:
        query = query.filter(status__in=query_object['status_int'])

    if len(query_object['card_type']) > 0:
        query = query.filter(card_type__in=query_object['card_type'])

    if len(query_object['cell']) > 0:
        query = query.filter(cell_name__in=query_object['cell'])

    if len(query_object['number']) > 0:
        query = query.filter(local_id__in=query_object['number'])

    if len(query_object['epic']) > 0:
        query = query.filter(epic_number__in=query_object['epic']) | \
                query.filter(epic_numbers__in=query_object['epic'])

    if len(query_object['epics']) > 0:
        query = query.filter(epic_numbers__in=query_object['epics'])

    if len(query_object['movedafter']) > 0:
        query = query.filter(last_moved__gt=to_date(query_object['movedafter'][0]))

    if len(query_object['movedbefore']) > 0:
        query = query.filter(last_moved__lt=to_date(query_object['movedbefore'][0]))

    if len(query_object['createdafter']) > 0:
        query = query.filter(created__gt=to_date(query_object['createdafter'][0]))

    if len(query_object['createdbefore']) > 0:
        query = query.filter(created__lt=to_date(query_object['createdbefore'][0]))

    if len(query_object['updatedbefore']) > 0:
        query = query.filter(modified__lt=to_date(query_object['updatedbefore'][0]))

    if len(query_object['updatedafter']) > 0:
        query = query.filter(modified__gt=to_date(query_object['updatedafter'][0]))

    if len(query_object['labels']) > 0:
        query = query.filter(labels__in=query_object['labels'])

    if len(query_object['contains']) > 0:
        query = query.filter(text__in=query_object['contains'])

    if len(query_object['tag']) > 0:
        query = query.filter(tags__in=query_object['tag'])

    if len(query_object['assignee']) > 0:
        query = query.filter(assignee__in=query_object['assignee'])

    if len(query_object['numeric_points']) > 0:
        query = query.filter(numeric_points__in=query_object['numeric_points'])

    if len(query_object['creator']) > 0:
        query = query.filter(creator__in=query_object['creator'])

    equivalent_orders = {"number":"local_id","points":"numeric_points","last modified":"modified","Assigned To":"assignee"}
    allowed_orders = ["local_id", "rank", "status", "numeric_points", "created", "modified", "assignee","-created", "-modified"]

    if len(query_object["order"]) > 0:
        order = query_object["order"][0].lower()
    else:
        order = "rank"
        
    logger.debug('FILTER: %s' %query)

    if order in equivalent_orders:
        order = equivalent_orders[order]
    if order in allowed_orders:
        return query.order_by(order).load_all()
    else:
        return query.order_by("rank").load_all()


