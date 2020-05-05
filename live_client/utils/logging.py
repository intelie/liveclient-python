# -*- coding: utf-8 -*-
import sys
from functools import partial
import logging as python_logging
from http.client import HTTPConnection
import multiprocessing
from pprint import pprint

from eliot import Message, write_traceback, add_destinations
from eliot.stdlib import EliotHandler

from live_client.connection.rest_input import async_event_sender

__all__ = ["debug", "info", "warn", "error", "exception", "log_to_live", "log_to_stdout"]

LOG_LEVELS = ["DEBUG", "INFO", "WARN", "ERROR", "EXCEPTION"]


default_level = "INFO"
log_level = default_level


def log_message(message, severity=None):
    if level_is_logged(severity):
        return Message.log(message_type=severity, message=message)


def exception(message):
    write_traceback(exc_info=sys.exc_info())


debug = partial(log_message, severity="debug")
info = partial(log_message, severity="info")
warn = partial(log_message, severity="warn")
error = partial(log_message, severity="error")


def log_to_live(message, log_function=None, event_type=None, min_level=default_level):
    message_severity = message.get("message_type", min_level)
    if level_is_logged(message_severity, min_level=min_level):
        message.update(__type=event_type)
        log_function(message)


def log_to_stdout(message, min_level=default_level):
    message_severity = message.get("message_type", min_level)
    if level_is_logged(message_severity, min_level=min_level):
        pprint(message)


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


def setup_live_logging(logging_settings, live_settings):
    event_type = logging_settings.get("event_type", "dda_log")
    level = logging_settings.get("level", default_level)

    username = live_settings.get("username")
    password = live_settings.get("password")
    logging_url = f"{live_settings['url']}{live_settings['rest_input']}"

    global log_level
    log_level = level
    log_function = async_event_sender(live_settings)

    if event_type and logging_url and username and password:
        add_destinations(
            partial(log_to_live, log_function=log_function, event_type=event_type, min_level=level)
        )


def setup_python_logging(logging_settings):
    level = logging_settings.get("level", default_level)

    log_level = getattr(python_logging, level.upper())

    if log_level is python_logging.DEBUG:
        HTTPConnection.debuglevel = 1

    python_logging.basicConfig()
    python_logging.getLogger().setLevel(log_level)
    python_logging.getLogger().addHandler(EliotHandler())

    requests_log = python_logging.getLogger("urllib3")
    requests_log.addHandler(EliotHandler())
    requests_log.setLevel(log_level)
    requests_log.propagate = False

    cometd_log = python_logging.getLogger("aiocometd")
    cometd_log.addHandler(EliotHandler())
    cometd_log.setLevel(log_level)
    cometd_log.propagate = False

    multiprocessing_log = multiprocessing.get_logger()
    multiprocessing_log.addHandler(EliotHandler())
    multiprocessing_log.setLevel(log_level)
    multiprocessing_log.propagate = False
