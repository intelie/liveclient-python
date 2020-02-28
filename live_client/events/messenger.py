# -*- coding: utf-8 -*-
import uuid
from enum import Enum

from . import raw
from live_client.connection.autodetect import build_sender_function
from live_client.utils.timestamp import get_timestamp
from live_client.utils import logging

__all__ = ["send_message", "maybe_send_message_event", "maybe_send_chat_message", "format_and_send"]


MESSAGE_TYPES = Enum("MESSAGE_TYPES", "EVENT, CHAT")
CONTROL_ACTIONS = Enum("CONTROL_ACTIONS", "ADD_USER, REMOVE_USER, JOIN, LEAVE")
EVENT_TYPES = {"message": "__message", "control": "__messenger_control"}


__all__ = [
    "join_messenger",
    "add_to_room",
    "remove_from_room",
    "send_message",
    "maybe_send_chat_message",
    "maybe_send_message_event",
]


def join_messenger(settings):
    connection_func = build_sender_function(settings["live"])

    bot_data = settings["output"]["author"]
    control_data = {
        "broadcast": True,
        "__skipstorage": True,
        "action": "user_joined_messenger",
        "user": bot_data,
    }

    event = format_event(EVENT_TYPES["control"], get_timestamp(), control_data)
    connection_func(event)


def add_to_room(settings, room_id, sender):
    return add_or_remove_from_room(settings, room_id, sender, action=CONTROL_ACTIONS.ADD_USER)


def remove_from_room(settings, room_id, sender):
    return add_or_remove_from_room(room_id, sender, settings, action=CONTROL_ACTIONS.REMOVE_USER)


def add_or_remove_from_room(settings, room_id, sender, action):
    connection_func = build_sender_function(settings["live"])

    control_data = {
        "action": "room_users_updated",
        "sender": sender,
        "addedOrUpdatedUsers": [],
        "removedUsers": [],
        "room": {"id": room_id},
    }

    bot_data = settings["output"]["author"]

    if action == CONTROL_ACTIONS.ADD_USER:
        control_key = "addedOrUpdatedUsers"
        bot_data.update(isNewUser=True, isAdmin=False)
    elif action == CONTROL_ACTIONS.REMOVE_USER:
        control_key = "removedUsers"

    control_data[control_key].append(bot_data)

    event = format_event(EVENT_TYPES["control"], get_timestamp(), control_data)
    connection_func(event)


def send_message(message, **kwargs):
    timestamp = kwargs.pop("timestamp", get_timestamp())
    message_type = kwargs.pop("message_type", None)

    if (message_type is None) or (message_type == MESSAGE_TYPES.EVENT):
        maybe_send_message_event(message, timestamp, **kwargs)

    if (message_type is None) or (message_type == MESSAGE_TYPES.CHAT):
        maybe_send_chat_message(message, **kwargs)


def maybe_send_message_event(message, timestamp, settings, **kwargs):
    output_settings = settings["output"]
    message_event = output_settings.get("message_event", {})
    event_type = message_event.get("event_type")
    messages_mnemonic = message_event.get("mnemonic")

    if event_type and messages_mnemonic:
        connection_func = build_sender_function(settings["live"])
        event = {"timestamp": timestamp, messages_mnemonic: {"value": message}}
        logging.debug("Sending message event '{}' for '{}'".format(event, event_type))
        raw.format_and_send(event, event_type, connection_func=connection_func)


def maybe_send_chat_message(message, settings, **kwargs):
    author_name = kwargs.get("author_name", None)

    output_settings = settings["output"]
    author = output_settings.get("author")
    room = kwargs.get("room", output_settings.get("room"))

    if (room is None) or (author is None):
        logging.warn(
            f"Cannot send message, room ({room}) and/or author ({author}) missing. Message is '{message}'"
        )

    else:
        connection_func = build_sender_function(settings["live"])

        if author_name:
            author.update(name=author_name)

        output_settings.update(room=room, author=author)
        logging.debug("Sending message '{}' from {} to {}".format(message, author, room))
        format_and_send(message, output_settings, connection_func=connection_func)


def format_and_send(message, settings, connection_func=None):
    timestamp = get_timestamp()
    event = format_message_event(timestamp, message, settings)

    logging.debug("Sending message {}".format(event))
    connection_func(event)


def format_message_event(timestamp, message, settings):
    room_data = settings["room"]
    author_data = settings["author"]

    message_data = {"message": message, "room": room_data, "author": author_data}

    return format_event(EVENT_TYPES["message"], timestamp, message_data)


def format_event(event_type, timestamp, event_data):
    base_event = {"__type": event_type, "uid": str(uuid.uuid4()), "createdAt": timestamp}
    base_event.update(event_data)
    return base_event
