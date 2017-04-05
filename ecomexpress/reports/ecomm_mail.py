import os
import sys

import settings

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders

from django.core.mail import EmailMultiAlternatives


def ecomm_send_mail(subject, link, to_mail_ids, content=None):
    s1 = smtplib.SMTP('i.prtouch.com', 26)
    for mail in to_mail_ids:
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = "Reports <support@ecomexpress.in>"
        if content:
            plain_test_part = MIMEText(content, 'plain')
        else:
            plain_test_part = MIMEText("Dear Team, \nPlease find  link to {0}. \n\n {1} \n\nRegards\n\nSupport Team".format(subject, link), 'plain')
        msg.attach(plain_test_part)
        msg['To']=mail
        s1.sendmail(msg['From'] , msg['To'], msg.as_string())
    s1.quit()
    return True

def ecomm_send_attach_mail(subject, file_name, to_mail_ids, content=None):
    full_path = '/home/web/ecomm.prtouch.com/ecomexpress/static/uploads/reports/'+file_name
    f = open(full_path, "r")
    file_content = f.read()
    f.close()

    attach = MIMEApplication(file_content, 'xlsx')
    attach.add_header('Content-Disposition', 'attachment', filename=file_name)

    s1 = smtplib.SMTP('i.prtouch.com', 26)
    for mail in to_mail_ids:
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = "Reports <support@ecomexpress.in>"
        if content:
            plain_test_part = MIMEText(content, 'plain')
        else:
            plain_test_part = MIMEText("Dear Team, \nPlease find the attached Report. \n\nRegards\n\nSupport Team", 'plain')
        msg.attach(plain_test_part)
        msg.attach(attach)
        msg['To']=mail
        s1.sendmail(msg['From'] , msg['To'], msg.as_string())
    s1.quit()
    return True

def ecomm_send_mail_content(subject, content, to_mail_ids):
    s1 = smtplib.SMTP('i.prtouch.com', 26)
    for mail in to_mail_ids:
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = "Support <support@ecomexpress.in>"
        plain_test_part = MIMEText(content, 'plain')
        msg.attach(plain_test_part)
        msg['To']=mail
        s1.sendmail(msg['From'] , msg['To'], msg.as_string())
    s1.quit()
    return True

