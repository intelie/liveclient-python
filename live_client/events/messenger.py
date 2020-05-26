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

    event = format_event(control_data, EVENT_TYPES["control"], get_timestamp())
    connection_func(event)


def add_to_room(settings, room_id, sender):
    return update_room_users(settings, room_id, sender, action=CONTROL_ACTIONS.ADD_USER)


def remove_from_room(settings, room_id, sender):
    return update_room_users(settings, room_id, sender, action=CONTROL_ACTIONS.REMOVE_USER)


def update_room_users(settings, room_id, sender, action):
    connection_func = build_sender_function(settings["live"])
    author = settings["output"]["author"]

    update_message_payload = create_room_update_data(room_id, sender, author, action)
    update_event = format_event(update_message_payload, EVENT_TYPES["control"], get_timestamp())
    connection_func(update_event)


def create_room_update_data(room_id, sender, author, action):
    target_collection = {
        CONTROL_ACTIONS.ADD_USER: "addedOrUpdatedUsers",
        CONTROL_ACTIONS.REMOVE_USER: "removedUsers",
    }

    data = {
        "action": "room_users_updated",
        "sender": sender,
        "addedOrUpdatedUsers": [],
        "removedUsers": [],
        "room": {"id": room_id},
    }

    if action == CONTROL_ACTIONS.ADD_USER:
        author.update(isNewUser=True, isAdmin=False)

    data[target_collection[action]].append(author)

    return data


def send_message(message, **kwargs):
    timestamp = kwargs.pop("timestamp", get_timestamp())
    message_type = kwargs.pop("message_type", None)

    if (message_type is None) or (message_type == MESSAGE_TYPES.EVENT):
        maybe_send_message_event(message, timestamp, kwargs.get("settings"))

    if (message_type is None) or (message_type == MESSAGE_TYPES.CHAT):
        maybe_send_chat_message(message, timestamp, **kwargs)


def maybe_send_message_event(message, timestamp, settings):
    output_settings = settings["output"]
    message_event = output_settings.get("message_event", {})
    event_type = message_event.get("event_type")
    messages_mnemonic = message_event.get("mnemonic")

    if event_type and messages_mnemonic:
        connection_func = build_sender_function(settings["live"])
        event = {"timestamp": timestamp, messages_mnemonic: {"value": message}}
        logging.debug("Sending message event '{}' for '{}'".format(event, event_type))
        raw.format_and_send(event, event_type, connection_func=connection_func)
        return True

    return False


def maybe_send_chat_message(message, timestamp, settings, **kwargs):
    output_settings = settings["output"]
    author = output_settings.get("author")
    room = kwargs.get("room", output_settings.get("room"))

    shall_send_message = (room is not None) and (author is not None)

    if not shall_send_message:
        logging.warn(f"Cannot send message, room ({room}) and/or author ({author}) missing")
        return False

    author["name"] = kwargs.get("author_name") or author.get("name")
    connection_func = build_sender_function(settings["live"])
    logging.debug("Sending message '{}' from {} to {}".format(message, author, room))
    format_and_send(message, room, author, timestamp=timestamp, connection_func=connection_func)
    return True


def format_and_send(message, room, author, timestamp, connection_func):
    event = format_message_event(message, room, author, timestamp=timestamp)
    logging.debug("Sending message {}".format(event))
    connection_func(event)


def format_message_event(message, room, author, timestamp):
    message_data = {"message": message, "room": room, "author": author}
    return format_event(message_data, EVENT_TYPES["message"], timestamp)


def format_event(event_data, event_type, timestamp):
    base_event = {"__type": event_type, "uid": str(uuid.uuid4()), "createdAt": timestamp}
    base_event.update(event_data)
    return base_event
