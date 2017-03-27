from apps.scrumdocelery import app

import datetime
from datetime import date


from apps.organizations.models import Organization
from apps.subscription.models import Subscription, SubscriptionStats, SpreedlyInfo, SubscriptionPlan
from apps.subscription.spreedly import Spreedly
from apps.classic.models import NewsItem as ClassicNewsItem
from apps.activities.models import NewsItem
from apps.projects import portfolio_managers

from decimal import Decimal
import traceback
import sys
import mixpanel
from django.conf import settings
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@app.task
def update_transactions():
        info = SpreedlyInfo.objects.get(id=1)
        spreedly = Spreedly()
        transactions = spreedly.getTransactions(info.last_transaction_fetched).getElementsByTagName("transaction")
        count = 0
        for transaction in transactions:
            try:
                trans_id = _getText(transaction.getElementsByTagName("id")[0])
                trans_succeeded = _getText(transaction.getElementsByTagName("succeeded")[0])
                trans_sub_id = int(_getText(transaction.getElementsByTagName("subscriber-customer-id")[0]))
                trans_amount = _getText(transaction.getElementsByTagName("amount")[0])
                trans_type = _getText(transaction.getElementsByTagName("detail-type")[0])
                transaction_time = _getText(transaction.getElementsByTagName("updated-at")[0])
                org = Organization.objects.get(id=trans_sub_id)
                info.last_transaction_fetched = int(trans_id)
                if trans_succeeded == "true" and trans_amount != "0.0":
                    org.subscription.total_revenue = org.subscription.total_revenue + Decimal(trans_amount)
                    org.subscription.save()
                    source = org.source.split("/")

                    try:
                        mp = mixpanel.Mixpanel(settings.MIXPANEL_TOKEN)
                        mp.people_track_charge(org.slug, trans_amount, {})
                        mp.track(org.slug, 'Billed', {
                            'Plan': org.subscription.plan.feature_level,
                            'Amount': trans_amount
                        })
                    except:
                        traceback.print_exc(file=sys.stdout)
                        logger.info("Could not update MIX")


                logger.debug("%s %s %s %s %s" % (trans_id, trans_succeeded, org.name, trans_amount, trans_type))
                count += 1
            except:
                pass

        logger.debug("Processed %d to transaction %d" % (count, info.last_transaction_fetched))
        info.save()


@app.task
def update_stats():
        spreedly = Spreedly()
        subscribers_result = spreedly.getSubscribers()
        subscribers = subscribers_result.getElementsByTagName("subscriber")
        trial = 0
        recurring = 0
        paid = 0
        expected = 0
        trial_rev = 0

        for subscriber in subscribers:
            if _getText(subscriber.getElementsByTagName("active")[0]) == "true":
                level = _getText(subscriber.getElementsByTagName("feature-level")[0])
                trial_user = ("true" == _getText(subscriber.getElementsByTagName("on-trial")[0]))
                recurring_user = ("true" == _getText(subscriber.getElementsByTagName("recurring")[0]))
                try:
                    planVersion = subscriber.getElementsByTagName("subscription-plan-version")[0]
                    planId = _getText(planVersion.getElementsByTagName("subscription-plan-id")[0])
                except IndexError:
                    continue

                if trial_user:
                    trial += 1
                else:
                    paid += 1
                if recurring_user:
                    # logger.debug( subscriber.toxml() )
                    try:
                        plan = SubscriptionPlan.objects.filter(spreedly_id=planId)[0]

                        recurring += 1
                        fee = plan.price_val
                        expected += fee
                        if trial_user:
                            trial_rev += fee
                    except:
                        logger.warn("Didn't know what to do with feature level %s" % level)

        today = date.today()
        for subscription in Subscription.objects.filter(is_trial=True, expires__gte=today):
            expected += subscription.plan.price_val
            trial_rev += subscription.plan.price_val

        stats = SubscriptionStats(trial_monthly_revenue="%f" % trial_rev, trial_orgs=trial, recurring_orgs=recurring,
                                  paid_orgs=paid, expected_monthly_revenue="%f" % expected,
                                  active_orgs=Organization.objects.count())
        stats.save()


def _getText(nodelist):
    rc = []
    for node in nodelist.childNodes:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)


@app.task
def archive_inactive_organizations():

    sixMonthsAgo = datetime.datetime.now() - datetime.timedelta(days=180)
    logger.debug("We are marking   %s (180 days) old organizations as inactive" % (sixMonthsAgo))

    for organization in Organization.objects.filter(active=True, created__lte=sixMonthsAgo):
        subscription = organization.subscription

        if subscription.is_trial and subscription.expires >= datetime.date.today():
            continue  # Active Trial  (why is it so old?  Hmmm...)
        news = NewsItem.objects.filter(project__organization=organization).order_by("-created")[:1]
        if len(news) > 0 and news[0].created > sixMonthsAgo:
            continue  # There was news, so there is active use in the past 6 months.

        classicNews = ClassicNewsItem.objects.filter(project__organization=organization).order_by("-created")[:1]
        if len(classicNews) > 0 and classicNews[0].created > sixMonthsAgo:
            continue  # There was news, so there is active use in the past 6 months.

        if subscription.token != '' and subscription.token is not None:
            continue  # anyone who paid, gets to stay

        logger.debug("Might want to deactivate : %s " % (organization.slug))
        organization.active = False

        # Update: Don't want to do this, we'll just make code check for org active
        for project in organization.projects.all():
            if project.project_type == 2:
                portfolio_managers.archive_portfolio_projects(project)
            project.active = False
            logger.debug("We are marking project : %s under organization : %s as inactive" % (project.slug, organization.slug))
            project.save()

        organization.save()
