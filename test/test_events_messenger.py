from unittest import mock

from testbase import *

from live_client.events import messenger
from predicates import *


class TestFormatEvent:
    def test_formatted_event_is_not_the_original(self):
        event = {}
        formatted_event = messenger.format_event("__type__", 0, event)
        assert event is not formatted_event

    def test_base_event_configured(self):
        required_keys = ["uid", "__type", "createdAt"]
        event = messenger.format_event({}, 0, "__type__")
        assert dict_has_valid_items(event, required_keys)

    def test_formatted_event_has_event_type(self):
        event_type = "__event_type__"
        event = messenger.format_event({}, 0, event_type)
        assert event.get("__type") == event_type

    def test_formatted_event_has_timestamp(self):
        timestamp = now_timestamp()
        event = messenger.format_event({}, timestamp, "_")
        assert event.get("createdAt") == timestamp
