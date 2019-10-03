# -*- coding: utf-8 -*-
from live_client.utils.timestamp import get_timestamp
from live_client.utils import logging

__all__ = [
    'format_event',
    'get_timestamp',
]


def create(event_type, event_data, process_settings=None, output_info=None):
    connection_func, output_settings = output_info
    logging.debug(f'Creating raw event of type "{event_type}": {event_data}')
    format_and_send(event_type, event_data, output_settings, connection_func=connection_func)


def format_and_send(event_type, event_data, settings, connection_func=None):
    timestamp = event_data.pop('timestamp', get_timestamp())
    event = format_event(timestamp, event_type, event_data, settings)
    connection_func(event, settings)


def format_event(timestamp, event_type, event_data, settings):
    event_data = event_data.copy()
    event_data['__type'] = event_type
    event_data['liverig__index__timestamp'] = timestamp
    return event_data
