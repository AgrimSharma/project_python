import datetime
from django.conf import settings
from pytz import timezone
from pytz.reference import UTC

import logging

logger = logging.getLogger(__name__)


SERVER_TZ = timezone(settings.TIME_ZONE)


# Returns today's date for the organization 
# Remember right now, it's not the same day across the world, so timezone counts!
def today(organization):
    try:
        return todayForTz(organization.timezone)
    except:
        logger.warn("Could not get today for organization")
        return datetime.date.today()


def todayForTz(timezone_str):
    utc_now = datetime.datetime.now(tz=UTC)
    tz = timezone(timezone_str)
    tz_now = utc_now.astimezone(tz)
    return tz_now.date()
    

# Takes a naive server date/time (our server runs in EST) and converts it to a
# naieve date/time that is in the organization's timezone.
# Only use this method to take a date/time and display it.  Don't try to store it
# or do math on it, that will just make your head hurt.
def toOrganizationTime(datetime, organization):
    return toTimezoneTime(datetime, organization.timezone)


def toTimezoneTime(datetime, timezone_str):
    tz = timezone(timezone_str)    
    servertime = SERVER_TZ.localize(datetime)
    return servertime.astimezone(tz)


def formatDateTime(datetime, organization, format="%b %d, %Y %I:%M %p"):
    if datetime is None:
        return ''
    local_time = toOrganizationTime(datetime, organization)
    return local_time.strftime(format)  # Format = Mar 23, 2012 1:05 am
    
def toFormat(date, toFormat="%Y-%m-%d", format="%Y-%m-%d %I:%M %p"):
    dt = datetime.datetime.strptime(date, format).strftime(toFormat)
    return dt
