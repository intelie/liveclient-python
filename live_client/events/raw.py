# -*- coding: utf-8 -*-
from live_client.utils.timestamp import get_timestamp
from live_client.utils import logging
from live_client.connection import autodetect

__all__ = ["format_event", "get_timestamp"]


def create(event_type, event_data, settings=None):
    connection_func = autodetect.build_sender_function(settings["live"])
    logging.debug(f'Creating raw event of type "{event_type}": {event_data}')
    format_and_send(event_type, event_data, connection_func=connection_func)


def format_and_send(event_type, event_data, connection_func=None):
    timestamp = event_data.pop("timestamp", get_timestamp())
    event = format_event(timestamp, event_type, event_data)
    connection_func(event)


def format_event(timestamp, event_type, event_data):
    event_data = event_data.copy()
    event_data["__type"] = event_type
    event_data["liverig__index__timestamp"] = timestamp
    return event_data
