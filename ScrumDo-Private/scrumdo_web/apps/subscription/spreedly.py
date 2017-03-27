# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.

import urllib2
from xml.dom.minidom import parse

from django.conf import settings

import logging

logger = logging.getLogger(__name__)


class Spreedly:
    API_VERSION = "v4"
    API_TOKEN = settings.SPREEDLY_API_TOKEN
    SITE_NAME = settings.SPREEDLY_SITE_NAME

    

    def updateSubscriptionPlan(self, organization, plan_id):
        url = "https://subs.pinpayments.com/api/%s/%s/subscribers/%d/change_subscription_plan.xml" % (Spreedly.API_VERSION, Spreedly.SITE_NAME, organization.id)
        logger.debug(url)
        auth_handler = urllib2.HTTPBasicAuthHandler()
        auth_handler.add_password(realm='Web Password',
                                  uri='https://subs.pinpayments.com/api',
                                  user=Spreedly.API_TOKEN,
                                  passwd='x')
        opener = urllib2.build_opener(auth_handler)
        urllib2.install_opener(opener)
        
        request = urllib2.Request(url, data="<subscription_plan><id>%d</id></subscription_plan>" % plan_id)
        request.add_header('Content-Type', 'application/xml')
        request.get_method = lambda: 'PUT'
        
        data = opener.open(request)
        
        logger.debug(data)

    # https://spreedly.com/api/[api_version]/[site_name]/subscribers/[customer_id].xml
    def getSubscriptionForOrganization(self, organization):
        url = "https://subs.pinpayments.com/api/%s/%s/subscribers/%d.xml" % (Spreedly.API_VERSION, Spreedly.SITE_NAME, organization.id)
        auth_handler = urllib2.HTTPBasicAuthHandler()
        auth_handler.add_password(realm='Web Password',
                                  uri='https://subs.pinpayments.com/api',
                                  user=Spreedly.API_TOKEN,
                                  passwd='x')
        opener = urllib2.build_opener(auth_handler)

        urllib2.install_opener(opener)
        result = urllib2.urlopen(url)
        data = parse(result)
        invoices = data.getElementsByTagName("invoices")[0]
        invoice_summaries = []
        for invoice in invoices.getElementsByTagName("invoice"):
            lineItems = invoice.getElementsByTagName("line-items")[0]
            lineItem = lineItems.getElementsByTagName("line-item")[0]

            i = {"date":getText(invoice.getElementsByTagName("created-at")[0].childNodes)[:10],
                 "token":getText(invoice.getElementsByTagName("token")[0].childNodes),
                 "price":getText(lineItem.getElementsByTagName("price")[0].childNodes),
                 "plan":getText(lineItem.getElementsByTagName("feature-level")[0].childNodes),
                 "duration":getText(lineItem.getElementsByTagName("description")[0].childNodes),
                 "balance":getText(invoice.getElementsByTagName("price")[0].childNodes),
                 "amount":getText(invoice.getElementsByTagName("amount")[0].childNodes)
                 }
            invoice_summaries.append(i)
        # 
        # <invoices type="array">
        #     <invoice>
        #       <closed type="boolean">true</closed>
        #       <created-at type="datetime">2011-03-20T18:38:00Z</created-at>
        #       <response-client-message nil="true"></response-client-message>
        #       <response-customer-message nil="true"></response-customer-message>
        #       <response-message nil="true"></response-message>
        #       <token>77d964f31f0a5f6ca798790e36f2b082d1f6b915</token>
        #       <updated-at type="datetime">2011-03-20T18:38:31Z</updated-at>
        #       <price>$14.95</price>
        #       <amount type="decimal">14.95</amount>
        #       <currency-code>USD</currency-code>
        #       <line-items type="array">
        #         <line-item>
        #           <amount type="decimal">14.95</amount>
        #           <currency-code>USD</currency-code>
        #           <description>Every 1 month</description>
        #           <notes nil="true"></notes>
        #           <price>$14.95</price>
        #           <feature-level>bronze</feature-level>
        #         </line-item>
        #       </line-items>
        #     </invoice>
        
        # logger.debug(data.toprettyxml())

        recurring = ("true" == getText(data.getElementsByTagName("recurring")[0].childNodes))
        account_active = ("true" == getText(data.getElementsByTagName("active")[0].childNodes))
        account_type = getText(data.getElementsByTagName("feature-level")[0].childNodes)
        active_until = getText(data.getElementsByTagName("active-until")[0].childNodes)
        try:
            plan_id = getText(data.getElementsByTagName("subscription-plan-id")[0].childNodes)
        except:
            plan_id = -1

        email = getText(data.getElementsByTagName("email")[0].childNodes)
        token = getText(data.getElementsByTagName("token")[0].childNodes)
        return {"plan_id":plan_id, "recurring":recurring, "account_active":account_active, "invoices":invoice_summaries, "account_type":account_type, "active_until":active_until, "email":email, "token":token}


    def getTransactions(self, since_id):
        url = "https://subs.pinpayments.com/api/v4/%s/transactions.xml?since_id=%d" % (Spreedly.SITE_NAME, since_id)
        auth_handler = urllib2.HTTPBasicAuthHandler()
        auth_handler.add_password(realm='Web Password',
                                  uri='https://subs.pinpayments.com/api',
                                  user=Spreedly.API_TOKEN,
                                  passwd='x')
        opener = urllib2.build_opener(auth_handler)

        urllib2.install_opener(opener)
        raw_data = urllib2.urlopen(url)
        logger.debug(raw_data)
        data = parse( raw_data  )
        return data
    
    def getPlans(self):
        url = "https://subs.pinpayments.com/api/%s/%s/subscription_plans.xml" % (Spreedly.API_VERSION, Spreedly.SITE_NAME)
        auth_handler = urllib2.HTTPBasicAuthHandler()
        auth_handler.add_password(realm='Web Password',
                                  uri='https://subs.pinpayments.com/api',
                                  user=Spreedly.API_TOKEN,
                                  passwd='x')
        opener = urllib2.build_opener(auth_handler)
        urllib2.install_opener(opener)
        raw_data = urllib2.urlopen(url)
        logger.debug(raw_data)
        data = parse( raw_data )
        return data
    

    #     GET /api/v4/[short site name]/subscribers.xml    
    def getSubscribers(self):
        url = "https://subs.pinpayments.com/api/%s/%s/subscribers.xml" % (Spreedly.API_VERSION, Spreedly.SITE_NAME)
        auth_handler = urllib2.HTTPBasicAuthHandler()
        auth_handler.add_password(realm='Web Password',
                                  uri='https://subs.pinpayments.com/api',
                                  user=Spreedly.API_TOKEN,
                                  passwd='x')
        opener = urllib2.build_opener(auth_handler)

        urllib2.install_opener(opener)
        data = parse(urllib2.urlopen(url)  )
        return data
    
    # https://spreedly.com/api/v4/meresheep/subscribers/444/stop_auto_renew.xml
    def stopAutoRenewForOrganization(self, organization):
        try:
            url = "https://subs.pinpayments.com/api/%s/%s/subscribers/%d/stop_auto_renew.xml" % (Spreedly.API_VERSION, Spreedly.SITE_NAME, organization.id)
            auth_handler = urllib2.HTTPBasicAuthHandler()
            auth_handler.add_password(realm='Web Password',
                                      uri='https://subs.pinpayments.com/api',
                                      user=Spreedly.API_TOKEN,
                                      passwd='x')
            opener = urllib2.build_opener(auth_handler)

            urllib2.install_opener(opener)
            urllib2.urlopen(url, "" )
        except urllib2.HTTPError:
            pass # subscriber ID not found, likely not a real subscription.





def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)
