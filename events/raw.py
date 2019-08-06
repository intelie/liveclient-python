# -*- coding: utf-8 -*-
from live_client.utils.timestamp import get_timestamp

__all__ = [
    'format_event',
    'get_timestamp',
]


def format_and_send(event_type, statuses, settings, connection_func=None):
    timestamp = statuses.pop('timestamp', get_timestamp())
    event = format_event(timestamp, event_type, statuses, settings)
    connection_func(event, settings)


def format_event(timestamp, event_type, statuses, settings):
    event_data = statuses.copy()
    event_data['__type'] = event_type
    event_data['liverig__index__timestamp'] = timestamp
    return event_data
