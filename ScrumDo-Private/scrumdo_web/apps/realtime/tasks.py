from apps.scrumdocelery import app
from django.conf import settings
from Pubnub import Pubnub
from django_redis import get_redis_connection

import json
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

MAX_SINGLE_MESSAGE_SIZE = 20000  # 32k limit with encoding, so lets stick to 20k without to be safe.

pubnub = Pubnub(
    settings.PUBNUB_PUB_KEY,  ## PUBLISH_KEY
    settings.PUBNUB_SUB_KEY,  ## SUBSCRIBE_KEY
    settings.PUBNUB_SEC_KEY,    ## SECRET_KEY
    False    ## SSL_ON?
)


@app.task
def send_messages(channelName):

    if settings.PUBNUB_PUB_KEY == 'x':
        return  # we set this to 'x' during automated tests and don't do real time during tests

    # Sends out batched messages
    # removes duplicates
    redis = get_redis_connection()


    key = "realtime-lock-%s" % channelName
    if redis.get(key):
        # we're locked out from sending, try again in 3 seconds
        logger.info("send_messages: channel is locked, trying again later.")
        send_messages.apply_async((channelName,), countdown=3)
        return


    key = "messages-%s" % channelName
    currentSize = 0
    messages = []
    sent = []
    while True:
        nextMessage = redis.lpop(key)
        logger.info("%s = %s" % (key, nextMessage) )
        if nextMessage is None:
            logger.info("Sending %d messages" % len(messages) )
            if len(messages) > 0:
                pubnub.publish({'channel': channelName,'message':messages})
            return
        nextMessage = json.loads(nextMessage)
        currentSize += len(nextMessage)
        if nextMessage in sent:
            logger.info("Not sending duplicate message %s" % nextMessage)
            continue  # duplicate
        messages.append(nextMessage)
        sent.append(nextMessage)
        if currentSize >= MAX_SINGLE_MESSAGE_SIZE:
            logger.info("Max Size: Sending %d messages" % len(messages) )
            pubnub.publish({'channel': channelName,'message':messages})
            messages = []




