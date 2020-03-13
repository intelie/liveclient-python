from unittest import mock

from testbase import *

from live_client.events import messenger
from predicates import *


def gen_settings(**kwargs):
    default_settings = {
        "output": {"author": {"name": "__default_name__"}, "room": "__room__"},
        "live": {},
    }
    default_settings.update(kwargs)
    return default_settings


class TestMaybeSendChatMessage:
    # If settings["output"] is not a dictionary -> Throw exception
    # If settings["output"]["author"] is not a dictionary -> Throw exception
    @mock.patch("live_client.connection.autodetect.build_sender_function", lambda _: no_action)
    @mock.patch("live_client.utils.logging.debug", no_action)
    @mock.patch("live_client.utils.logging.warn", no_action)
    def test_invalid_settings_throws(self):
        # Must fail if "output" attribute missing
        settings = {}
        assert raises(KeyError, messenger.maybe_send_chat_message, "_", settings)

    # Message shall be sent if:
    #   (1) author is configured in settings and
    #   (2) room is configured either in kwargs or in settings
    @mock.patch("live_client.events.messenger.build_sender_function", lambda _: Collector())
    @mock.patch("live_client.utils.logging.debug", no_action)
    @mock.patch("live_client.utils.logging.warn", no_action)
    def test_message_should_be_sent(self):
        settings = {"output": {"author": {}, "room": "__room__"}, "live": {}}

        message_sent = messenger.maybe_send_chat_message("_", settings)
        assert message_sent

    @mock.patch("live_client.utils.logging.debug", no_action)
    @mock.patch("live_client.utils.logging.warn", no_action)
    def test_message_not_sent_if_no_room(self):
        settings = {"output": {"author": {}}, "live": {}}
        collector = Collector()
        with mock.patch("live_client.events.messenger.build_sender_function", lambda _: collector):
            message_sent_1 = messenger.maybe_send_chat_message("_", settings)
            assert not message_sent_1 and collector.is_empty()

        settings["output"]["room"] = None
        collector = Collector()
        with mock.patch("live_client.events.messenger.build_sender_function", lambda _: collector):
            message_sent_2 = messenger.maybe_send_chat_message("_", settings)
            assert not message_sent_2 and collector.is_empty()

    @mock.patch("live_client.utils.logging.debug", no_action)
    @mock.patch("live_client.utils.logging.warn", no_action)
    def test_message_not_sent_if_no_author(self):
        settings = {"output": {"room": "__room__"}, "live": {}}
        collector = Collector()
        with mock.patch("live_client.events.messenger.build_sender_function", lambda _: collector):
            message_sent_1 = messenger.maybe_send_chat_message("_", settings)
            assert not message_sent_1 and collector.is_empty()

        settings["output"]["author"] = None
        collector = Collector()
        with mock.patch("live_client.events.messenger.build_sender_function", lambda _: collector):
            message_sent_2 = messenger.maybe_send_chat_message("_", settings)
            assert not message_sent_2 and collector.is_empty()

    # If kwargs contains "author_name" then "author" name shall be updated.
    @mock.patch("live_client.utils.logging.debug", no_action)
    @mock.patch("live_client.utils.logging.warn", no_action)
    def test_author_name_updates_author(self):
        settings = gen_settings()
        new_author_name = "__new_author__"
        assert settings["output"]["author"]["name"] != new_author_name
        collector = Collector()
        with mock.patch("live_client.events.messenger.build_sender_function", lambda _: collector):
            messenger.maybe_send_chat_message("_", settings, author_name=new_author_name)
        assert collector.buffer[0]["author"]["name"] == new_author_name

    # If message can be sent:
    #   log success message (debug)
    #   call sender function
    @mock.patch("live_client.utils.logging.debug", no_action)
    @mock.patch("live_client.utils.logging.warn", no_action)
    def test_sender_called_on_success(self):
        settings = gen_settings()
        collector = Collector()
        with mock.patch("live_client.events.messenger.build_sender_function", lambda _: collector):
            messenger.maybe_send_chat_message("_", settings)
            assert not collector.is_empty()

    #   return True
    @mock.patch("live_client.events.messenger.build_sender_function", lambda _: no_action)
    @mock.patch("live_client.utils.logging.debug", no_action)
    @mock.patch("live_client.utils.logging.warn", no_action)
    def test_returns_true_on_success(self):
        settings = gen_settings()
        ret = messenger.maybe_send_chat_message("_", settings)
        assert ret is True

    # Else:
    #   log error message (warn)
    #   return False
    @mock.patch("live_client.events.messenger.build_sender_function", lambda _: no_action)
    @mock.patch("live_client.utils.logging.debug", no_action)
    @mock.patch("live_client.utils.logging.warn", no_action)
    def test_returns_true_on_success(self):
        settings = gen_settings(output={})
        ret = messenger.maybe_send_chat_message("_", settings)
        assert ret is False


class TestFormatAndSend:
    def mock_connection_func(self, event):
        self.event_data = event

    @mock.patch("live_client.utils.logging.debug")
    def test_message_logged(self, debug_mock):
        message = "_"
        room = "_"
        author = {}
        connection_func = self.mock_connection_func

        messenger.format_and_send(message, room, author, connection_func)
        debug_mock.assert_called_with("Sending message {}".format(self.event_data))

    def test_connection_func_called(self):
        message = "__message__"
        room = "__room__"
        author = {}
        messenger.format_and_send(message, room, author, self.mock_connection_func)
        assert (
            self.event_data["message"] == message
            and self.event_data["room"] == room
            and self.event_data["author"] == author
            and self.event_data.get("createdAt") is not None
            and self.event_data.get("uid") is not None
            and self.event_data.get("__type") is not None
        )


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
