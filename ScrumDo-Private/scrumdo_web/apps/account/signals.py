from django.db.models.signals import post_save
from django.dispatch import receiver

from mailer.models import Message
from apps.scrumdo_mailer.tasks import setupQueue


@receiver(post_save, sender=Message, dispatch_uid="reset_password")
def reset_password(sender, instance, **kwargs):
    # Send task to celery
    setupQueue(sender, instance=instance)