from django import template
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.html import escape

from apps.organizations.models import Organization
from apps.projects.models import Story
from apps.activities.models import NewsItem
import apps.projects.limits as limits
from apps.subscription.models import Subscription, AttachmentExtra
from apps.projects.templatetags.projects_tags import probable_email
from django.conf import settings

from apps.classic import models as classic_models


import hashlib
import datetime
import time 

register = template.Library()

import logging

logger = logging.getLogger(__name__)


@register.inclusion_tag('subscription/mixpanel.html', takes_context=True)
def mixpanel_register_snippet(context):
    try:
        organization = context["organization"]
        if not organization:
            return {"display": False}

        if not settings.USE_MIXPANEL:
            return {"display": False}

        today = datetime.date.today()
        mdiff = datetime.timedelta(days=-30)
        date_30days_Agoago = today + mdiff

        activity30day = NewsItem.objects.filter(created__gte=date_30days_Agoago, project__organization=organization).count()
        classicactivity30day = classic_models.NewsItem.objects.filter(created__gte=date_30days_Agoago, project__organization=organization).count()
        totalActivity = NewsItem.objects.filter(project__organization=organization).count()
        subscription = organization.subscription

        g1 = str(organization.id % 2)
        g2 = str(organization.id % 3)
        g3 = str(organization.id % 4)
        g4 = str(organization.id % 5)

        return {'30dayactivity': activity30day,
                '30dayclassicactivity': classicactivity30day,
                'totalactivity': totalActivity,
                'projects': subscription.projectsUsed(),
                'users': subscription.usersUsed(),
                'istrial': subscription.is_trial,
                'paid': subscription.total_revenue > 0 and subscription.active,
                'trialmonth': organization.created.strftime('%Y-%m'),
                'trialweek': organization.created.strftime('%Y-%U'),
                'source': organization.source,
                'plan': subscription.planName(),
                'price': subscription.planPrice(),
                'TestGroup1': g1,
                'TestGroup2': g2,
                'TestGroup3': g3,
                'TestGroup4': g4,
                'display': True
                }
    except:
        return {"display": False}


@register.inclusion_tag('subscription/intercom-in-app-msg.html', takes_context=True)
def customer_in_app_msg(context, org):  
    try:
        user = context["user"]
        if not user.is_active:
            return {"display": False}

        if not settings.USE_INTERCOM:
            return {"display": False}

        subscription = org.subscription
        if not subscription.is_trial and subscription.plan.premium_plan:
            return {
                "display": True,
                "INTERCOM_APP_ID": settings.INTERCOM_APP_ID,
                "user": user
            }
        else:
            return {"display": False}
    except: 
        return {'display': False}


@register.inclusion_tag('subscription/customer.io.html',takes_context=True)
def customer_io_snippet(context):   
    try:
        user = context["user"]
        if not user.is_active:
            return {"display": False}

        if not settings.USE_INTERCOM:
            return {"display": False}

        verified_email = user.email != None and len(user.email) > 0
        join_timestamp = int(time.mktime(user.date_joined.timetuple()))
        org_created = 0
        orgs = Organization.getOrganizationsForUser(user)
            
        user_hash = hashlib.sha1('u10qdyll' + probable_email(user) ).hexdigest()
        g1 = g2 = g3 = g4 = -1
        if len(orgs) > 0:
            org = sorted(orgs,key=lambda org:org.subscription.plan.price_val)[len(orgs)-1] 
            org_created = int(time.mktime(org.created.timetuple()))

            g1 = org.id % 2
            g2 = org.id % 3
            g3 = org.id % 4
            g4 = org.id % 5

        else:
            org = None
        return {'org_count': len(orgs),
                'org_created': org_created,
                'staff': org.hasStaffAccess(user) ,
                'join_timestamp': join_timestamp,
                "user": user,
                "org": org,
                "display": True,
                "production":not settings.DEBUG,
                "user_hash": user_hash,
                "test_group_1": g1,
                "test_group_2": g2,
                "test_group_3": g3,
                "test_group_4": g4,
                "verified_email": verified_email,
                "INTERCOM_APP_ID": settings.INTERCOM_APP_ID
        }
    except:
        return {"display": False}




@register.tag
def canupload(parser, token):
    tag_name, obj = token.split_contents()
    nodelist = parser.parse(('endcanupload',))
    parser.delete_first_token()
    return LimitNode(nodelist, obj, limits.org_storage_limit)

class LimitNode(template.Node):
    def __init__(self, nodelist, obj, limit):
        self.nodelist = nodelist
        self.obj = obj
        self.limit = limit

    def render(self, context):
        obj = context[self.obj]        
        self.limit.increaseAllowed(organization=obj)
        try:
            if self.limit.increaseAllowed(organization=obj):
                return self.nodelist.render(context)
            else:
                return ""
        except:
            return "**ERROR**"
    
    

@register.tag
def noupload(parser, token):
    tag_name, obj = token.split_contents()
    nodelist = parser.parse(('endnoupload',))
    parser.delete_first_token()
    return NoUploadNode(nodelist, obj)

class NoUploadNode(template.Node):
    def __init__(self, nodelist, obj):
        self.nodelist = nodelist
        self.obj = obj
    def render(self, context):
        obj = context[self.obj]
        sub = Subscription.getSubscriptionForObject(obj)
        if sub and sub.canUpload():
            return ""
        else:
            return self.nodelist.render(context)

@register.filter
def daysuntil(date):
    return max(0, (date - datetime.date.today()).days)

# @register.filter
# def show_file_thumb(f):
#     return mark_safe("""<a href="#" onclick="openOverlay('%s'); return false;">%s</a>""" % ( view_url, escape(' '.join(file_string))))
    
    
@register.filter
def show_file(f, next):
    logger.debug(f.canPreview())
    view_url = reverse("view_attachment", kwargs={"attachment_pk":f.pk, "next":next})
    file_string = [f.filename]
    return mark_safe("""<a href="#" onclick="openOverlay('%s'); return false;">%s</a>""" % ( view_url, escape(' '.join(file_string))))

@register.filter
def show_file_loc(f):
    file_string = []
    if f.extra.related_organization:
        file_string.append("%s"%f.extra.related_organization.name)
    if f.extra.related_project:
        file_string.append("/ %s"%f.extra.related_project.name)
    if f.extra.related_iteration:
        file_string.append("/ %s"%f.extra.related_iteration.name)
    try:
        object = f.extra.attachment.content_type.get_object_for_this_type(id = f.extra.attachment.object_id)
        if isinstance(object, Story):
            file_string.append("/ Story %s-%d" % (object.project.prefix, object.local_id))
    except:
        pass
        
    return ' '.join(file_string)
    
@register.filter
def version(f):
    version = AttachmentExtra.objects.filter(related_id=f.extra.related_id).count()
        
    return 'version %s'%version


#    sub = Subscription.getSubscriptionForObject(f.content_object)
#    if not sub.canUpload(): # this means you are above your quota
#        return mark_safe(escape(f.filename) + " <a title='You must return to a higher subscription level or delete some files in order to return to below your quota and regain access to files.' href='#'>" + silk("help") + "</a>")
#    else:
#        return mark_safe('<a href="' + f.attachment_file.url + '" target="_blank">' + escape(f.filename) + '</a>')
