# -*- coding: utf-8 -*-
from functools import partial

from . import rest_input, tcp_input

__all__ = ["send_event"]


def has_required_keys(settings, key_list):
    return all([item in settings for item in key_list])


def send_event(event, live_settings=None):
    if live_settings is None:
        live_settings = {}

    if has_required_keys(live_settings, rest_input.REQUIRED_PARAMETERS):
        sender_function = rest_input.send_event
    elif has_required_keys(live_settings, tcp_input.REQUIRED_PARAMETERS):
        sender_function = tcp_input.send_event
    else:
        raise ValueError(
            "Invalid settings. The keys '{}' or '{}' must be defined".format(
                rest_input.REQUIRED_PARAMETERS, tcp_input.REQUIRED_PARAMETERS
            )
        )

    sender_function(event, live_settings=live_settings)


def build_sender_function(live_settings):
    return partial(send_event, live_settings=live_settings)
