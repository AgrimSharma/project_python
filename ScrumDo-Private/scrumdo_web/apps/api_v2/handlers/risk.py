from .common import *
from django.db.models import Q, Sum
from django.utils.html import strip_tags
from apps.projects import portfolio_managers, managers as project_managers
from apps.projects.models import Risk, Portfolio, Story, Project, Iteration, TeamIterationWIPLimit
from apps.projects.access import read_access_or_403, write_access_or_403
from haystack.query import SearchQuerySet
import apps.projects.systemrisks as systemrisks

def lookup_prefix(projects, story):
    possible = [p for p in projects if p.id==story.project_id]
    if len(possible) == 0:
        return ''
    return possible[0].prefix

class RiskTargetSearch(BaseHandler):
    allowed_methods = ('GET',)



    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, portfolio_id):
        portfolio = Portfolio.objects.get(id=portfolio_id)
        project = portfolio.root
        read_access_or_403(project, request.user)

        query = request.GET.get('query', '').lower()
        projects = list(Project.objects.filter(portfolio_level__portfolio=portfolio, project_type = Project.PROJECT_TYPE_KANBAN)) + [project]
        projects = [p for p in projects if has_read_access(p, request.user)]

        iteration_list = []
        cards_list = []

        if query:
            iterations = Iteration.objects.filter(project__in=projects, name__icontains=query).select_related('project')
            iteration_list = [{'name': i.name, 'project': i.project.name, "id":i.id, "slug":i.project.slug} for i in iterations]

            card_query = SearchQuerySet()
            card_query = card_query.models(Story)
            card_query = card_query.filter(project_id__in=[p.id for p in projects])
            card_query = card_query.filter(text=query)
            cards_list = [{
                             'id': c.object.id,
                             'summary': c.object.summary,
                             'number': c.object.local_id,
                             'prefix': lookup_prefix(projects, c.object)
                          } for c in card_query.order_by("local_id").load_all()[:100]]

            projects = [p for p in projects if (query.lower() in p.name.lower())]

        project_list = [{'name': p.name, 'slug': p.slug, 'color':p.color, 'icon':p.icon} for p in projects]

        return {
            'query': query,
            'projects': project_list,
            'iterations': iteration_list,
            'cards': cards_list
        }


class RiskHandler(BaseHandler):
    allowed_methods = ('GET','POST','DELETE','PUT')
    write_fields = (
        "description",
        "probability",
        "severity_1",
        "severity_2",
        "severity_3",
        "severity_4",
        "severity_5",
        "severity_6",
        "severity_7")

    fields = (
        "id",
        "portfolio_id",
        "description",
        "probability",
        "severity_1",
        "severity_2",
        "severity_3",
        "severity_4",
        "severity_5",
        "severity_6",
        "severity_7",
        "cards",
        "iterations",
        ("projects", ("name", "slug", "color", "icon"))
    )
    model = Risk

    @staticmethod
    def iterations(risk):
        return [
            {
                'id': i.id,
                'name': i.name,
                'project': i.project.name,
                'project_slug': i.project.slug

            }
            for i in risk.iterations.all().select_related('project')
        ]

    @staticmethod
    def cards(risk):
        return [
            {
                'id': card.id,
                'number': card.local_id,
                'summary': card.summary,
                'project_slug': card.project.slug,
                'prefix': card.project.prefix
            }
            for card in risk.cards.all().select_related('project')
        ]

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def update(self, request, organization_slug, portfolio_id, risk_id):
        portfolio = Portfolio.objects.get(id=portfolio_id)
        portfolio_project = portfolio.root
        read_access_or_403(portfolio_project, request.user)
        risk = Risk.objects.get(portfolio=portfolio, id=risk_id)
        self._update_risk_fields(risk, request.data)
        risk.cards = []
        risk.iterations = []
        risk.projects = []
        self._update_artifacts(risk, request.data, portfolio, request.user)
        risk.save()
        return risk

    @throttle(WRITE_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_writes')
    def delete(self, request, organization_slug, portfolio_id, risk_id):
        portfolio = Portfolio.objects.get(id=portfolio_id)
        portfolio_project = portfolio.root
        read_access_or_403(portfolio_project, request.user)
        risk = Risk.objects.get(portfolio=portfolio, id=risk_id)
        risk.delete()
        return "OK"

    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, portfolio_id):
        portfolio = Portfolio.objects.get(id=portfolio_id)
        portfolio_project = portfolio.root
        read_access_or_403(portfolio_project, request.user)

        iteration_id = request.GET.get('iterationId', None)
        story_id = request.GET.get('storyId', None)
        project_slug = request.GET.get('projectSlug', None)

        iteration = iteration_id and Iteration.objects.get(id=iteration_id)
        story = story_id and Story.objects.get(id=story_id)
        # check if we got portfolio root as project query
        if project_slug is not None and project_slug == portfolio_project.slug:
            project_slug = None

        project = project_slug and Project.objects.get(slug=project_slug, portfolio_level__portfolio=portfolio)

        criteria = Q(projects=portfolio_project)

        if project:
            criteria = Q(projects=project) | Q(iterations__project=project) | Q(cards__project=project)

        if iteration:
            criteria = criteria | Q(iterations=iteration) | Q(projects=iteration.project) | Q(cards__iteration=iteration)

        if story:
            criteria = Q(cards=story)

        return Risk.objects.filter(portfolio=portfolio).filter(criteria).distinct().order_by("-probability")


    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def create(self, request, organization_slug, portfolio_id):
        data = request.data
        portfolio = Portfolio.objects.get(id=portfolio_id)
        project = portfolio.root

        read_access_or_403(project, request.user)
        risk = Risk(portfolio=portfolio)
        self._update_risk_fields(risk, data)
        risk.save()

        self._update_artifacts(risk, data, portfolio, request.user)

        return risk

    def _update_artifacts(self, risk, data, portfolio, user):

        for card in data.get('cards', []):
            self._add_card(risk, card['id'], portfolio, user)

        for iteration in data.get('iterations', []):
            self._add_iteration(risk, iteration['id'], portfolio, user)

        for project in data.get('projects', []):
            self._add_project(risk, project['slug'], portfolio, user)


    def _add_card(self, risk, card_id, portfolio, user):
        card = Story.objects.filter(id=card_id).select_related('project')[0]
        write_access_or_403(card.project, user)
        if not portfolio_managers.is_project_in_portfolio(card.project, portfolio):
            return
        risk.cards.add(card)

    def _add_iteration(self, risk, iteration_id, portfolio, user):
        iteration = Iteration.objects.filter(id=iteration_id).select_related('project')[0]
        write_access_or_403(iteration.project, user)
        if not portfolio_managers.is_project_in_portfolio(iteration.project, portfolio):
            return
        risk.iterations.add(iteration)

    def _add_project(self, risk, project_slug, portfolio, user):
        project = Project.objects.get(slug=project_slug)
        write_access_or_403(project, user)
        if not portfolio_managers.is_project_in_portfolio(project, portfolio):
            return
        risk.projects.add(project)


    def _update_risk_fields(self, risk, data):
        for fieldname in RiskHandler.write_fields:
            value = data.get(fieldname, None)
            if value is not None:
                setattr(risk, fieldname, value)


class SystemRiskHandler(BaseHandler):
    allowed_methods = ("GET", )

    @throttle(READ_THROTTLE_REQUESTS, THROTTLE_TIME, 'user_reads')
    def read(self, request, organization_slug, project_slug, iteration_id=None):
        
        org, project = checkOrgProject(request, organization_slug, project_slug, False)
        if iteration_id is not None:
            iteration = project.iterations.get(id=iteration_id)
        
            return systemrisks.systemRisks(project, iteration)
        else:
            project_risks = []
            iterations = project.iterations.filter(iteration_type=Iteration.ITERATION_WORK, hidden=False)
            for iteration in iterations:
                risks = systemrisks.systemRisks(project, iteration)
                project_risks = project_risks + risks
            return project_risks
