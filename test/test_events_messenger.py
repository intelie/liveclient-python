from unittest import mock

from testbase import *

from live_client.events import messenger
from predicates import *
from mocks import *


def gen_settings(**kwargs):
    default_settings = {
        "output": {"author": {"id": 1, "name": "__default_name__"}, "room": "__room__"},
        "live": {},
    }
    default_settings.update(kwargs)
    return default_settings


class TestJoinMessenger:
    def test_correct_action_sent(self):
        settings = gen_settings()

        connection_mock = mock.Mock()
        with patch_with_factory(
            "live_client.events.messenger.build_sender_function", connection_mock
        ):
            messenger.join_messenger(settings)
            event = connection_mock.call_args[0][0]
            assert event["action"] == "user_joined_messenger"

    def test_correct_author_sent(self):
        settings = gen_settings()
        author = settings["output"]["author"]

        connection_mock = mock.Mock()
        with patch_with_factory(
            "live_client.events.messenger.build_sender_function", connection_mock
        ):
            messenger.join_messenger(settings)
            event = connection_mock.call_args[0][0]
            assert event["user"] == author


class TestAddToRoom:
    def test_correct_action_sent(self):
        settings = gen_settings()
        connection_mock = mock.Mock()

        with patch_with_factory(
            "live_client.events.messenger.build_sender_function", connection_mock
        ):
            messenger.add_to_room(settings, 0, "_")
            event = connection_mock.call_args[0][0]
            assert event["action"] == "room_users_updated"

    def test_user_is_added(self):
        user = {"id": 2, "name": "__local_test__"}
        settings = gen_settings()
        settings["output"]["author"] = user

        room_id = 1
        chat_mock = ChatMock()
        with patch_with_factory(
            "live_client.events.messenger.build_sender_function", chat_mock.update_room
        ):
            messenger.add_to_room(settings, room_id, "Tester")

            assert chat_mock.room != {}
            assert chat_mock.room["users"][user["id"]]["name"] == user["name"]

    def test_user_is_not_removed(self):
        user = {"id": 1, "name": "__local_test__"}
        settings = gen_settings()
        settings["output"]["author"] = user

        room_id = 1
        existing_user = {"id": 2, "name": "__should_remain__"}
        chat_mock = ChatMock()
        chat_mock.add_user(existing_user)
        with patch_with_factory(
            "live_client.events.messenger.build_sender_function", chat_mock.update_room
        ):
            messenger.add_to_room(settings, room_id, "Tester")
            assert (
                not is_empty(chat_mock.room["users"])
                and chat_mock.room["users"][2]["name"] == existing_user["name"]
            )


class TestRemoveFromRoom:
    def test_correct_action_sent(self):
        settings = gen_settings()
        connection_mock = mock.Mock()

        with patch_with_factory(
            "live_client.events.messenger.build_sender_function", connection_mock
        ):
            messenger.remove_from_room(settings, 0, "_")
            event = connection_mock.call_args[0][0]
            assert event["action"] == "room_users_updated"

    def test_user_is_removed(self):
        user = {"id": 2, "name": "__local_test__"}
        settings = gen_settings()
        settings["output"]["author"] = user

        room_id = 1
        chat_mock = ChatMock()
        chat_mock.room["users"][2] = user
        with patch_with_factory(
            "live_client.events.messenger.build_sender_function", chat_mock.update_room
        ):
            messenger.remove_from_room(settings, room_id, "Tester")
            assert chat_mock.room["users"] == {}

    def test_user_is_not_removed(self):
        user = {"id": 1, "name": "__local_test__"}
        settings = gen_settings()
        settings["output"]["author"] = user

        room_id = 1
        existing_user = {"id": 2, "name": "__should_remain__"}
        chat_mock = ChatMock()
        chat_mock.add_user(existing_user)
        with patch_with_factory(
            "live_client.events.messenger.build_sender_function", chat_mock.update_room
        ):
            messenger.remove_from_room(settings, room_id, "Tester")
            assert (
                bool(chat_mock.room["users"])
                and chat_mock.room["users"][2]["name"] == existing_user["name"]
            )


class TestUpdateRoomUsers:
    def test_user_is_added(self):
        user = {"id": 2, "name": "__local_test__"}
        settings = gen_settings()
        settings["output"]["author"] = user

        room_id = 1
        chat_mock = ChatMock()
        with patch_with_factory(
            "live_client.events.messenger.build_sender_function", chat_mock.update_room
        ):
            messenger.update_room_users(
                settings,
                room_id=room_id,
                sender="Tester",
                action=messenger.CONTROL_ACTIONS.ADD_USER,
            )

            assert len(chat_mock.room) > 0
            assert chat_mock.room["users"][user["id"]]["name"] == user["name"]

    def test_user_is_removed(self):
        user = {"id": 2, "name": "__local_test__"}
        settings = gen_settings()
        settings["output"]["author"] = user

        room_id = 1
        chat_mock = ChatMock()
        chat_mock.room["users"][2] = user
        with patch_with_factory(
            "live_client.events.messenger.build_sender_function", chat_mock.update_room
        ):
            messenger.update_room_users(
                settings,
                room_id=room_id,
                sender="Tester",
                action=messenger.CONTROL_ACTIONS.REMOVE_USER,
            )

            assert chat_mock.room["users"] == {}


class TestSendMessage:
    @mock.patch("live_client.events.messenger.maybe_send_message_event")
    @mock.patch("live_client.events.messenger.maybe_send_chat_message")
    def test_correct_implementation_called(self, chat_mock, event_mock):
        def reset_mocks():
            nonlocal event_mock, chat_mock
            event_mock.reset_mock()
            chat_mock.reset_mock()

        # None shall be called:
        messenger.send_message("_", message_type="")
        assert not event_mock.called and not chat_mock.called
        reset_mocks()

        # send event shall be called:
        messenger.send_message("_", message_type=messenger.MESSAGE_TYPES.EVENT)
        assert event_mock.called and not chat_mock.called
        reset_mocks()

        # send chat shall be called:
        messenger.send_message("_", message_type=messenger.MESSAGE_TYPES.CHAT)
        assert not event_mock.called and chat_mock.called
        reset_mocks()

        # both shall be called:
        messenger.send_message("_", message_type=None)
        assert event_mock.called and chat_mock.called


class TestMaybeSendMessageEvent:
    # If settings["output"] is not a dictionary -> Throw exception
    def test_invalid_settings_throws(self):
        settings = {}
        assert raises(KeyError, messenger.maybe_send_message_event, "_", 0, settings)

    # Message shall be sent if:
    #   1 - event_type is not None and
    #   2 - messages_mnemonic is not None
    # Event must follow the template: event = {"timestamp": timestamp, messages_mnemonic: {"value": message}}
    @mock.patch("live_client.utils.logging.debug", no_action)
    def test_message_should_be_sent(self):
        messages_mnemonic = "__mnemonic__"

        settings = gen_settings()
        settings["output"]["message_event"] = {
            "event_type": "__event_type__",
            "mnemonic": messages_mnemonic,
        }
        collector = Collector()
        with patch_with_factory("live_client.events.messenger.build_sender_function", collector):
            message = "_"
            timestamp = get_timestamp()
            message_sent = messenger.maybe_send_message_event(message, timestamp, settings)
            assert message_sent

            sent_event = collector[0]
            assert sent_event.get("liverig__index__timestamp") == timestamp
            assert sent_event.get(messages_mnemonic) is not None
            assert sent_event.get(messages_mnemonic).get("value") == message

    def test_message_not_sent_if_no_event_type(self):
        settings = gen_settings()
        settings["output"]["message_event"] = {"mnemonic": "_"}
        collector = Collector()
        with mock.patch("live_client.events.messenger.build_sender_function", lambda _: collector):
            message = "_"
            timestamp = get_timestamp()
            message_sent = messenger.maybe_send_message_event(message, timestamp, settings)
            assert not message_sent
            assert collector.is_empty()

    def test_message_not_sent_if_no_messages_mnemonic(self):
        settings = gen_settings()
        settings["output"]["message_event"] = {"event_type": "__event_type__"}
        collector = Collector()
        with mock.patch("live_client.events.messenger.build_sender_function", lambda _: collector):
            message = "_"
            timestamp = get_timestamp()
            message_sent = messenger.maybe_send_message_event(message, timestamp, settings)
            assert not message_sent
            assert collector.is_empty()


class TestMaybeSendChatMessage:
    # If settings["output"] is not a dictionary -> Throw exception
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
        timestamp = get_timestamp()

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
        timestamp = get_timestamp()
        event = messenger.format_event({}, "_", timestamp)
        assert event.get("createdAt") == timestamp
