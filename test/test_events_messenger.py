from unittest import mock

from testbase import *

from live_client.events import messenger
from predicates import *


class TestFormatMessageEvent:
    def test_event_configured(self):
        message = "__message__"
        room = "__room__"
        author = {}
        timestamp = now_timestamp()

        base_message = {"message": message, "room": room, "author": author}
        event = messenger.format_message_event(message, room, author, timestamp)

        assert dict_contains(event, base_message) and event.get("createdAt") == timestamp


class TestFormatEvent:
    # [ECS]: Do we really need to create a new dict? <<<<<
    def test_formatted_event_is_not_the_original(self):
        event = {}
        formatted_event = messenger.format_event(event, "__type__", 0)
        assert event is not formatted_event

    def test_base_event_configured(self):
        required_keys = ["uid", "__type", "createdAt"]
        event = messenger.format_event({}, "__type__", 0)
        assert dict_has_valid_items(event, required_keys)

    def test_formatted_event_has_event_type(self):
        event_type = "__event_type__"
        event = messenger.format_event({}, event_type, 0)
        assert event.get("__type") == event_type

    def test_formatted_event_has_timestamp(self):
        timestamp = now_timestamp()
        event = messenger.format_event({}, "_", timestamp)
        assert event.get("createdAt") == timestamp
