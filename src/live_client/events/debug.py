# -*- coding: utf-8 -*-
import json

from live_client.utils.timestamp import get_timestamp

__all__ = ["format_and_send"]


def format_and_send(event_type, statuses, output_settings):
    timestamp = get_timestamp()
    event = format_event(timestamp, event_type, statuses)
    print("-----------------------------------------------------")
    print(json.dumps(event))


def format_event(timestamp, event_type, statuses):
    event_data = statuses.copy()
    event_data["__type"] = event_type
    event_data["liverig__index__timestamp"] = timestamp
    return json.dumps(event_data)
