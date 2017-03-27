from apps.scrumdocelery import app
from rollbardecorator import logexception

import mixpanel
from django.conf import settings

@app.task
def logEvent(organization_slug, eventName, data):
    mp = mixpanel.Mixpanel(settings.MIXPANEL_TOKEN)
    mp.track(organization_slug, eventName, data)