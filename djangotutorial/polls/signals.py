from logging import getLogger

from django.contrib.admin.models import LogEntry
from django.db.models.signals import post_save
from django.dispatch import receiver

from mysite.utils import make_log

security_logger = getLogger("django.security")


@receiver(post_save, sender=LogEntry)
def write_logentry_message(
    sender: object,
    instance: "LogEntry",
    created: bool,  # noqa: FBT001
    **kwargs: object,
) -> None:
    event_information = {
        "msg": f"LogEntry {instance.pk} was {'created' if created else 'updated'}\n",
        "action_time": instance.action_time,
        "user": instance.user,
        "content_type": instance.content_type,
        "object_id": instance.object_id,
        "object_repr": instance.object_repr,
        "action_flag": instance.action_flag,
        "change_message": instance.change_message,
        "sender": sender,
        "kwargs": kwargs,
    }

    make_log(
        logger=security_logger,
        message=event_information,
        level="info",
    )
