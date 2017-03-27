import datetime as dt
import apps.organizations.signals as signals
import mixpanel

from django.template import defaultfilters
from apps.subscription.tutorial import createTutorialProject
from apps.projects import signals as project_signals
from .models import Organization, Team


class OrganizationMixin(object):
    """ Organization models mixin
    """

    def create_organization(self, org_name):
        slug = defaultfilters.slugify( org_name )[:45]
        c = 0
        while True:
            try:
                org = Organization.objects.get(slug=slug)
                c += 1
                slug = "%s%d" % (defaultfilters.slugify( org.name )[:45], c)
            except Organization.DoesNotExist:
                break # finally found a slug that doesn't exist

        organization = Organization()
        organization.name = org_name
        organization.slug = slug
        organization.creator = self.request.user
        organization.save()
        signals.organization_created.send(sender=self.request, organization=organization )    
        return organization

    def set_trial(self, organization):
        subscription = organization.subscription
        subscription.plan_id = 3043  # 3043 = Premium 100 user plan
        subscription.expires = dt.date.today() + dt.timedelta(days=30)
        subscription.is_trial = True
        subscription.had_trial = True
        subscription.save()
        return subscription

    def create_teams(self, organization):
        member_team = Team(organization = organization, name="Members", access_type="write")
        member_team.save()
        
        staff_team = Team(organization = organization, name="Account Owner", access_type="staff")
        staff_team.save()
        staff_team.members.add(self.request.user)
        return member_team, staff_team

    def add_source(self, organization):
        try:
            cookie = self.request.COOKIES.get("__utmz")
            if re.search("utmgclid", cookie) == None:
                # Referrer based source
                source = re.search("utmcsr=([^|]+)",cookie).group(1)
                mode = re.search("utmcmd=([^|]+)",cookie).group(1)
                organization.source = "%s / %s" % (source, mode)
            else:
                # Adwords based source?
                source = re.search("utmgclid=([^|]+)",cookie).group(1)
                mode = re.search("utmctr=([^|]+)",cookie).group(1)
                organization.source = "Adwords / %s / %s" % (source, mode)
        except:
            organization.source = ""
        organization.save()  

    def create_tutorial(self, organization):
        tut = createTutorialProject(organization, self.request.user)
        project_signals.project_created.send(sender=self.request, project=tut, user=self.request.user)
        return tut

