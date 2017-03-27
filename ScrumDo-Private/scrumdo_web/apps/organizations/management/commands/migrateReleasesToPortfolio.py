#!/usr/bin/env python
from django.core.management import BaseCommand

from apps.organizations.models import Organization 
from apps.projects.models import Project, Portfolio
from apps.projects import managers as project_manager, portfolio_managers

import logging
logger = logging.getLogger(__name__)

class Command(BaseCommand):

    def handle(self, *args, **options):
        #get all organizations
        organizations = Organization.objects.all()

        for organization in organizations:
            #get portfolio projects for organization
            releases = Project.objects.filter(organization=organization,
                                              project_type=Project.PROJECT_TYPE_PORTFOLIO,
                                              active=True)

            for root in releases:
                #check if already have an associated portfolio
                #ignore if Yes 
                if Portfolio.objects.filter(root=root).count() == 0:
                    projects = root.children.filter(personal=False)
                    
                    root.icon = 'fa-folder'
                    root.save()
                    
                    portfolio = Portfolio(root=root, organization=organization)
                    portfolio.save()

                    level = portfolio_managers.create_portfolio_level(portfolio, 'Projects', 1, 'fa-bullseye')

                    for project in projects:
                        portfolio_managers.add_project_to_portfolio(level, project, userAction = False)