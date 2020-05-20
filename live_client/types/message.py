# -*- coding: utf-8 -*-
from collections import UserDict
from datetime import datetime
from pytz import timezone

from live_client.utils import logging

__all__ = ["Message"]


class Message(UserDict):
    def __init__(self, message_event):
        created_at = None
        try:
            author_timezone = timezone(message_event.get("timeZone", "UTC"))
            created_at = author_timezone.localize(
                datetime.fromtimestamp(int(message_event.get("createdAt")) / 1000)
            )
        except (TypeError, ValueError) as e:
            logging.exception(e)

        message_event.update(text=message_event.get("message", ""), created_at=created_at)

        super().__init__(message_event)

    def has_mention(self, name):
        return name in self.data.get("text")

    def remove_mentions(self, name):
        self.data["text"] = self.data["text"].replace(name, "")
        return self

    def serialize(self):
        return self.data
