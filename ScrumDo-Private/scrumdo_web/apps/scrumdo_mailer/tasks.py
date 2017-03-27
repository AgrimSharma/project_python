# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2012 ScrumDo LLC
# All rights reserved.  This file may not be used, distributed, nor modified without
# explicit permission from ScrumDo LLC.

import time
import smtplib
import traceback

from django.db.models.signals import post_save
from django.conf import settings
from django.core.mail import send_mail as core_send_mail

from apps.scrumdocelery import app
from mailer.models import MessageLog, Message, DontSendEntry
from celery.utils.log import get_task_logger
from socket import error as socket_error

logger = get_task_logger(__name__)


@app.task
def sendEmails(message_id):
    send_one(message_id)
    try:
        pass
    except:
        stack = traceback.extract_stack()
        logger.error(stack)


def send_one(message_id):
    start_time = time.time()

    dont_send = 0
    deferred = 0
    sent = 0
    messages = Message.objects.filter(id=message_id)
    for message in messages:
        if DontSendEntry.objects.has_address(message.to_address):
            logger.info("skipping email to %s as on don't send list " % message.to_address.encode("utf-8"))
            MessageLog.objects.log(message, 2) # @@@ avoid using literal result code
            message.delete()
            dont_send += 1
        else:
            try:
                logger.info("sending message '%s' to %s" % (message.subject.encode("utf-8"), message.to_address.encode("utf-8")))
                core_send_mail(message.subject, message.message_body, message.from_address, [message.to_address])
                MessageLog.objects.log(message, 1) # @@@ avoid using literal result code
                message.delete()
                sent += 1
            except (socket_error, smtplib.SMTPSenderRefused, smtplib.SMTPRecipientsRefused, smtplib.SMTPAuthenticationError), err:
                message.defer()
                logger.info("message deferred due to failure: %s" % err)
                MessageLog.objects.log(message, 3, log_message=str(err)) # @@@ avoid using literal result code
                deferred += 1

    logger.info("")
    logger.info("%s sent; %s deferred; %s don't send" % (sent, deferred, dont_send))
    logger.info("done in %.2f seconds" % (time.time() - start_time))
    

def setupQueue(sender, **kwargs):
    obj = kwargs['instance']
    sendEmails.apply_async((obj.id,), countdown=3)


if __name__=="scrumdo_mailer.tasks" and settings.USE_QUEUE:
    post_save.connect(setupQueue, sender=Message, dispatch_uid="mailer_queue_tasks")
    