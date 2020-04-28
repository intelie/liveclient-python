# -*- coding: utf-8 -*-
import requests
from multiprocessing import get_context as get_mp_context

from requests.exceptions import RequestException, ConnectionError
from setproctitle import setproctitle
from eliot import start_action

from live_client.utils import logging
from live_client.utils import network

__all__ = ["send_event"]

REQUIRED_PARAMETERS = ["url", "username", "password", "rest_input"]


def create_session(username, password):
    session = requests.Session()
    session.auth = (username, password)
    return session


def _validate_settings(live_settings):
    if not isinstance(live_settings, dict):
        raise Exception(
            f"Invalid type for 'live_settings'. 'dict' expected, got '{type(live_settings)}'"
        )

    for param in REQUIRED_PARAMETERS:
        if live_settings.get(param) is None:
            raise Exception(f"Invalid settings. Missing '{param}' field")


def send_event(event, live_settings):
    if not event:
        return False

    try:
        _validate_settings(live_settings)
    except Exception as e:
        logging.exception(e)
        raise

    if live_settings.get("session") is None:
        new_session = create_session(live_settings["username"], live_settings["password"])
        live_settings.update(session=new_session)

    session = live_settings["session"]
    verify_ssl = live_settings.get("verify_ssl", True)
    url = f"{live_settings['url']}{live_settings['rest_input']}"

    try:
        with network.ensure_timeout(network.getcontext().default_timeout):
            response = session.post(url, json=event, verify=verify_ssl)
            response.raise_for_status()
    except RequestException as e:
        logging.exception("ERROR: Cannot send event, {}<{}>".format(e, type(e)))
        logging.exception("Event data: {}".format(event))
        raise

    return True


def async_send(queue, live_settings):
    with start_action(action_type="async_logger"):
        logging.info("Remote logger process started")
        setproctitle("DDA: Remote logger")

        live_settings.update(
            session=create_session(live_settings["username"], live_settings["password"])
        )
        while True:
            event = queue.get()
            if event is None:
                # Flush queue and exit loop:
                while not queue.empty():
                    queue.get(block=False)
                break
            send_event(event, live_settings)


def async_event_sender(live_settings):
    return AsyncSender(live_settings)


def is_available(live_settings):
    try:
        _validate_settings(live_settings)
    except Exception as e:
        return False, ["Not configured", str(e)]

    session = create_session(live_settings["username"], live_settings["password"])
    url = f"{live_settings['url']}{live_settings['rest_input']}"
    verify_ssl = live_settings.get("verify_ssl", True)
    ssl_message = f'TLS certificate validation is {verify_ssl and "enabled" or "disabled"}'

    try:
        response = session.get(url, verify=verify_ssl)
        response.raise_for_status()
    except ConnectionError as e:
        rest_input_available = False
        messages = [str(e), ssl_message]
    except RequestException as e:
        rest_input_available = e.response.status_code == 405
        messages = [
            rest_input_available and f"status={e.response.status_code}" or str(e),
            ssl_message,
        ]
    else:
        rest_input_available = False
        messages = ["No result", ssl_message]

    return rest_input_available, messages


class AsyncSender:
    def __init__(self, live_settings):
        mp = get_mp_context("fork")
        self.events_queue = mp.Queue()
        self.process = mp.Process(target=async_send, args=(self.events_queue, live_settings))
        self.process.start()

    def send(self, event):
        self.events_queue.put(event)

    def __call__(self, event):
        return self.send(event)

    def finish(self):
        self.send(None)
