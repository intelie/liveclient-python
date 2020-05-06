# -*- coding: utf-8 -*-
import uuid

from live_client.connection import autodetect
from live_client.utils.timestamp import get_timestamp
from live_client.utils import logging
from .constants import DEFAULT_ANNOTATION_DURATION

__all__ = ["create", "format_and_send"]


def create(annotation_data, settings=None, room=None):
    output_settings = settings["output"]
    connection_func = autodetect.build_sender_function(settings["live"])

    if room is None:
        room = output_settings["room"]

    output_settings.update(
        room=room, author=output_settings["author"], dashboard=output_settings.get("dashboard", {})
    )
    format_and_send(annotation_data, output_settings, connection_func=connection_func)


def format_and_send(annotation_data, settings, connection_func=None):
    timestamp = annotation_data.get("timestamp", get_timestamp())
    event = format_event(timestamp, annotation_data, settings)

    logging.debug("Creating annotation {}".format(event))
    connection_func(event)


def format_event(timestamp, annotation_data, settings):
    author_data = settings["author"]
    room_data = settings["room"]
    dashboard_data = settings["dashboard"]

    message_event = annotation_data.copy()
    message_event.update(
        __type="__annotations",
        __src=message_event.get("__src", "live_agent"),
        uid=message_event.get("uid", str(uuid.uuid4())),
        createdAt=int(message_event.get("createdAt", timestamp)),
        author=author_data.get("name"),
        room=room_data,
        dashboardId=dashboard_data.get("id"),
        dashboard=dashboard_data.get("name"),
        searchable=True,
    )

    begin = int(message_event.get("begin", timestamp))

    end = message_event.pop("end", None)
    if (end is None) or end < begin:
        end = begin + DEFAULT_ANNOTATION_DURATION

    message_event.update(begin=begin)
    message_event.update(end=int(end))

    def has_invalid_value(key):
        return message_event.get(key, -1) in (0, None)

    if any(map(has_invalid_value, ("begin", "end", "createdAt"))):
        logging.warn("Invalid annotation: {}".format(message_event))
        return

    return message_event
