from .cfd import calculateCFD, calculateBacklogCFD
from .lead import calculateLeadTime, calculateIncrementLeadTime
from .movement import calculateMovements
from .burn import calculateBurn, calculateLegacyIterationBurn, calculateLegacyProjectBurn
from .aging import calculateAging

from apps.organizations import tz
from django_redis import get_redis_connection
import datetime
import json


def json_default(obj):
    """Default JSON serializer to handle date/times "2015-03-31T12:21:04",."""
    if isinstance(obj, datetime.datetime):
        return obj.strftime("%Y-%m-%dT%H:%M:%S")
    if isinstance(obj, datetime.date):
        return obj.strftime("%Y-%m-%d")
    return str(obj)


def get_cached_saved_report(report, organization=None, iteration_id=None):
    if organization is None:
        organization = report.project.organization
    today = tz.today(organization)
    cache_key = report.cache_key(today, iteration_id)
    redis = get_redis_connection('default')
    data = redis.get(cache_key)

    return json.loads(data) if data is not None else data


def cache_saved_report(report, data, organization=None, iteration_id=None):
    if organization is None:
        organization = report.project.organization
    today = tz.today(organization)
    cache_key = report.cache_key(today, iteration_id)

    redis = get_redis_connection('default')

    # We only want to cache this for today, but because of timezones the time left "today" could vary
    now = tz.toOrganizationTime(datetime.datetime.now(), organization)
    seconds_left_today = (24-now.hour) * 3600 - (60-now.minute) * 60  # to the nearest minute is close enough

    redis.setex(cache_key, seconds_left_today, json.dumps(data, default=json_default))