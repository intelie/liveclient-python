from unittest import mock

from testbase import *

from live_client.events import raw


DEFAULT_EVENT = {}
A_TIMESTAMP = 1582927835001
DEFAULT_TIMESTAMP = 0


class TestCreateEvent:
    @mock.patch("live_client.connection.autodetect.build_sender_function", lambda _: no_action)
    @mock.patch("live_client.utils.logging.debug")
    def test_message_logged(self, debug_mock):
        event_type = "__event_type__"
        event_data = {}
        settings = {"live": "__live__"}
        raw.create(event_type, event_data, settings)
        debug_mock.assert_called_with(f'Creating raw event of type "{event_type}": {event_data}')

    @mock.patch("live_client.utils.logging.debug", no_action)
    def test_event_sent(self):
        buffer = []

        def collect(event):
            nonlocal buffer
            buffer.append(event)

        with mock.patch(
            "live_client.connection.autodetect.build_sender_function", lambda _: collect
        ):
            event_type = "__event_type__"
            event_data = {"data": {}}
            settings = {"live": "__live__"}

            raw.create(event_type, event_data, settings)

            assert len(buffer) > 0
            assert buffer[0]["data"] is event_data["data"]


class TestFormatEvent:
    def test_formatted_event_is_not_the_original(self):
        event = DEFAULT_EVENT
        formatted_event = raw.format_event(event, 0, "_")
        assert event is not formatted_event

    def test_formatted_event_has_event_type(self):
        event_type = "__event_type__"
        event = raw.format_event(DEFAULT_EVENT, event_type, "_")
        assigned_type = event.get("__type")
        assert assigned_type is not None and assigned_type == event_type

    def test_formatted_event_has_timestamp(self):
        timestamp = get_timestamp()
        event = raw.format_event(DEFAULT_EVENT, "_", timestamp)
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
