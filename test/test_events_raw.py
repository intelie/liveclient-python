from testbase import *
from live_client.events import raw


DEFAULT_EVENT = {}
A_TIMESTAMP = 1582927835001
DEFAULT_TIMESTAMP = 0


class TestFormatEvent:
    def test_formatted_event_is_not_the_original(self):
        event = DEFAULT_EVENT
        formatted_event = raw.format_event(event, 0, "_")
        assert event is not formatted_event

    def test_formatted_event_has_event_type(self):
        event_type = "__event_type__"
        event = raw.format_event(DEFAULT_EVENT, "_", event_type)
        assigned_type = event.get("__type")
        assert assigned_type is not None and assigned_type == event_type

    def test_formatted_event_has_timestamp(self):
        timestamp = now_timestamp()
        event = raw.format_event(DEFAULT_EVENT, timestamp, "_")
        assigned_timestamp = event.get("liverig__index__timestamp")
        assert assigned_timestamp is not None and assigned_timestamp == timestamp


class TestFormatAndSend:
    event_data = None

    def mock_connection_func(self, event):
        self.event_data = event

    def test_timestamp_prop_is_removed(self):
        raw.format_and_send({"timestamp": "_"}, "_", self.mock_connection_func)
        assert self.event_data.get("timestamp") is None

    def test_timestamp_is_formatted(self):
        raw.format_and_send({"timestamp": "_"}, "_", self.mock_connection_func)
        assert self.event_data.get("liverig__index__timestamp") is not None

    def test_timestamp_is_inserted(self):
        raw.format_and_send({}, "_", self.mock_connection_func)
        assert self.event_data.get("liverig__index__timestamp") is not None
