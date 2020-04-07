# -*- coding: utf-8 -*-
import uuid

from live_client.connection import autodetect
from live_client.utils.timestamp import get_timestamp
from live_client.utils import logging
from .constants import DEFAULT_ANNOTATION_DURATION

__all__ = ["create"]


def create(annotation_data, settings, room=None):
    send_event = autodetect.build_sender_function(settings["live"])

    output_settings = settings["output"].copy()
    room = room or output_settings["room"]
    output_settings.update(room=room, dashboard=output_settings.get("dashboard", {}))

    annotation_event = _build_annotation_event(
        annotation_data,
        output_settings.get("author"),
        output_settings.get("room"),
        output_settings.get("dashboard"),
    )
    logging.debug("Creating annotation {}".format(annotation_event))
    send_event(annotation_event)


def _build_annotation_event(annotation_data, author, room, dashboard):
    # TODO: [ECS] I think here we can just assume 0 or None should cause this
    # function to fill the annotation with the default values, so we can drop
    # the check below
    if any([_is_invalid_timestamp(annotation_data.get(field, -1)) for field in ["begin", "createdAt"]]):
        return None

    timestamp = get_timestamp()
    message_event = annotation_data.copy()
    message_event.update(
        __type="__annotations",
        __src=message_event.get("__src", "live_agent"),
        uid=message_event.get("uid", str(uuid.uuid4())),
        createdAt=int(message_event.get("createdAt") or timestamp),
        author=author.get("name"),
        room=room,
        dashboardId=dashboard.get("id"),
        dashboard=dashboard.get("name"),
        searchable=True,
    )

    begin = int(message_event.get("begin") or timestamp)
    end = int(message_event.pop("end", None) or -1)
    if end < begin:
        end = begin + DEFAULT_ANNOTATION_DURATION
    message_event.update(begin=begin, end=end)

    return message_event


def _is_invalid_timestamp(ts):
    return ts == 0 or ts == None
