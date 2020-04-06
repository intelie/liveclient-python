# -*- coding: utf-8 -*-
import uuid

from live_client.connection import autodetect
from live_client.utils.timestamp import get_timestamp
from live_client.utils import logging
from .constants import DEFAULT_ANNOTATION_DURATION

__all__ = ["create", "format_and_send"]


def create(annotation_data, settings, room=None):
    send_event = autodetect.build_sender_function(settings["live"])

    output_settings = settings["output"].copy()
    room = room or output_settings["room"]
    output_settings.update(room=room, dashboard=output_settings.get("dashboard", {}))

    annotation_event = build_annotation_event(
        annotation_data,
        output_settings.get("author"),
        output_settings.get("room"),
        output_settings.get("dashboard"),
    )
    logging.debug("Creating annotation {}".format(annotation_event))
    send_event(annotation_event)


def build_annotation_event(annotation_data, author, room, dashboard):
    timestamp = get_timestamp()
    message_event = annotation_data.copy()
    message_event.update(
        __type="__annotations",
        __src=message_event.get("__src", "live_agent"),
        uid=message_event.get("uid", str(uuid.uuid4())),
        createdAt=int(message_event.get("createdAt", timestamp)),
        author=author.get("name"),
        room=room,
        dashboardId=dashboard.get("id"),
        dashboard=dashboard.get("name"),
        searchable=True,
    )

    begin = int(message_event.get("begin", timestamp))
    end = int(message_event.pop("end", -1))
    if end < begin:
        end = begin + DEFAULT_ANNOTATION_DURATION
    message_event.update(begin=begin, end=end)

    def has_invalid_value(key):
        return message_event.get(key, -1) in (0, None)

    if any(map(has_invalid_value, ("begin", "end", "createdAt"))):
        logging.warn(f"Invalid annotation: {message_event}")
        return

    return message_event
