# -*- coding: utf-8 -*-
from live_client.utils.timestamp import get_timestamp
from live_client.utils import logging
from live_client.connection import autodetect

__all__ = ["create"]


def create(event_type, event_data, settings):
    connection_func = autodetect.build_sender_function(settings["live"])
    logging.debug(f'Creating raw event of type "{event_type}": {event_data}')
    format_and_send(event_data, event_type, connection_func=connection_func)


def format_and_send(event_data, event_type, connection_func):
    timestamp = event_data.pop("timestamp", get_timestamp())
    event = format_event(event_data, event_type, timestamp)
    connection_func(event)


def format_event(event_data, event_type, timestamp):
    event_data = event_data.copy()
    event_data["__type"] = event_type
    event_data["liverig__index__timestamp"] = timestamp
    return event_data
