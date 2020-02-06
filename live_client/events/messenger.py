# -*- coding: utf-8 -*-
import uuid
from enum import Enum

from . import raw
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


def join_messenger(process_name, process_settings, output_info):
    connection_func, output_settings = output_info

    bot_data = process_settings["destination"]["author"]
    control_data = {
        "broadcast": True,
        "__skipstorage": True,
        "action": "user_joined_messenger",
        "user": bot_data,
    }

    event = format_event(EVENT_TYPES["control"], get_timestamp(), control_data, output_settings)
    connection_func(event, output_settings)


def add_to_room(process_name, process_settings, output_info, room_id, sender):
    return add_or_remove_from_room(
        process_name,
        process_settings,
        output_info,
        room_id,
        sender,
        action=CONTROL_ACTIONS.ADD_USER,
    )


def remove_from_room(process_name, process_settings, output_info, room_id, sender):
    return add_or_remove_from_room(
        room_id,
        sender,
        process_name,
        process_settings,
        output_info,
        action=CONTROL_ACTIONS.REMOVE_USER,
    )


def add_or_remove_from_room(process_name, process_settings, output_info, room_id, sender, action):
    connection_func, output_settings = output_info

    control_data = {
        "action": "room_users_updated",
        "sender": sender,
        "addedOrUpdatedUsers": [],
        "removedUsers": [],
        "room": {"id": room_id},
    }

    bot_data = process_settings["destination"]["author"]

    if action == CONTROL_ACTIONS.ADD_USER:
        control_key = "addedOrUpdatedUsers"
        bot_data.update(isNewUser=True, isAdmin=False)
    elif action == CONTROL_ACTIONS.REMOVE_USER:
        control_key = "removedUsers"

    control_data[control_key].append(bot_data)

    event = format_event(EVENT_TYPES["control"], get_timestamp(), control_data, output_settings)
    connection_func(event, output_settings)


def send_message(process_name, message, timestamp, **kwargs):
    message_type = kwargs.pop("message_type", None)

    if (message_type is None) or (message_type == MESSAGE_TYPES.EVENT):
        maybe_send_message_event(process_name, message, timestamp, **kwargs)

    if (message_type is None) or (message_type == MESSAGE_TYPES.CHAT):
        maybe_send_chat_message(process_name, message, **kwargs)


def maybe_send_message_event(process_name, message, timestamp, **kwargs):
    process_settings = kwargs.get("process_settings", {})
    output_info = kwargs.get("output_info", None)

    destination_settings = process_settings["destination"]
    message_event = destination_settings.get("message_event", {})
    event_type = message_event.get("event_type")
    messages_mnemonic = message_event.get("mnemonic")

    if event_type and messages_mnemonic:
        connection_func, output_settings = output_info
        event = {"timestamp": timestamp, messages_mnemonic: {"value": message}}
        logging.debug(
            "{}: Sending message event '{}' for '{}'".format(process_name, event, event_type)
        )
        raw.format_and_send(event_type, event, output_settings, connection_func=connection_func)


def maybe_send_chat_message(process_name, message, **kwargs):
    author_name = kwargs.get("author_name", None)
    process_settings = kwargs.get("process_settings", {})
    output_info = kwargs.get("output_info", None)

    destination_settings = process_settings["destination"]
    room = kwargs.get("room", destination_settings.get("room"))
    author = destination_settings.get("author")

    if (room is None) or (author is None):
        logging.warn(
            "{}: Cannot send message, room ({}) and/or author ({}) missing. Message is '{}'",
            process_name,
            room,
            author,
            message,
        )

    else:
        connection_func, output_settings = output_info

        if author_name:
            author.update(name=author_name)

        output_settings.update(room=room, author=author)
        logging.debug(
            "{}: Sending message '{}' from {} to {}".format(process_name, message, author, room)
        )
        format_and_send(message, output_settings, connection_func=connection_func)


def format_and_send(message, settings, connection_func=None):
    timestamp = get_timestamp()
    event = format_message_event(timestamp, message, settings)

    logging.debug("Sending message {}".format(event))
    connection_func(event, settings)


def format_message_event(timestamp, message, settings):
    room_data = settings["room"]
    author_data = settings["author"]

    message_data = {"message": message, "room": room_data, "author": author_data}

    return format_event(EVENT_TYPES["message"], timestamp, message_data, settings)


def format_event(event_type, timestamp, event_data, settings):

    base_event = {"__type": event_type, "uid": str(uuid.uuid4()), "createdAt": timestamp}
    base_event.update(event_data)
    return base_event
