# -*- coding: utf-8 -*-
import sys
from functools import partial

from eliot import Message, write_traceback, add_destinations

from live_client.connection.rest_input import async_event_sender

__all__ = [
    'debug',
    'info',
    'warn',
    'error',
    'exception',
    'log_to_live',
]

LOG_LEVELS = [
    'DEBUG',
    'INFO',
    'WARN',
    'ERROR',
    'EXCEPTION',
]


default_level = 'INFO'
log_level = default_level


def log_message(message, severity=None):
    if level_is_logged(severity):
        return Message.log(message_type=severity, message=message)


def exception(message):
    write_traceback(exc_info=sys.exc_info())


debug = partial(log_message, severity='debug')
info = partial(log_message, severity='info')
warn = partial(log_message, severity='warn')
error = partial(log_message, severity='error')


def log_to_live(message, log_function=None, event_type=None, min_level=None):
    message_severity = message.get('message_type', min_level)
    if level_is_logged(message_severity, min_level=min_level):
        message.update(__type=event_type)
        log_function(message)


def setup_live_logging(settings):
    log_settings = settings.get('output', {}).get('rest-log', {})

    event_type = log_settings.get('event_type', 'dda_log')
    url = log_settings.get('url')
    username = log_settings.get('username')
    password = log_settings.get('password')
    level = log_settings.get('level', default_level)

    global log_level
    log_level = level
    log_function = async_event_sender({'url': url, 'username': username, 'password': password})

    if event_type and url and username and password:
        add_destinations(
            partial(
                log_to_live,
                log_function=log_function,
                event_type=event_type,
                min_level=level,
            )
        )


def level_is_logged(message_severity, min_level=None):
    severity = message_severity.upper()
    if severity in LOG_LEVELS:
        message_severity_idx = LOG_LEVELS.index(severity)

        if (min_level is None) or (min_level.upper() not in LOG_LEVELS):
            min_level = log_level
        else:
            min_level = min_level.upper()

        min_level_idx = LOG_LEVELS.index(min_level.upper())

        result = message_severity_idx >= min_level_idx
    else:
        result = True

    return result
