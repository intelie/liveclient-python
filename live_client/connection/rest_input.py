# -*- coding: utf-8 -*-
import requests
from multiprocessing import Process, Queue

from requests.exceptions import RequestException, ConnectionError
from setproctitle import setproctitle
from eliot import start_action

from live_client.utils import logging
from live_client.utils.network import retry_on_failure

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
        with retry_on_failure(3.05, max_retries=5):
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

        # live_settings["session"] = None
        # FIXME: We don't need this call here. send_event will handle the session, we just need to invalidate it here
        live_settings.update(
            session=create_session(live_settings["username"], live_settings["password"])
        )
        while True:
            event = queue.get()
            if event is None:
                break
            send_event(event, live_settings)


def async_event_sender(live_settings):
    events_queue = Queue()
    # FIXME: [ECS] We need a way to access the process handle below outside this function:
    # [ECS] Update: Now "async_send" exits the message loop if None is received. We still
    # need to provide the process handle to the external world, but at least now we have
    # a bit of control over the running process.
    process = Process(target=async_send, args=(events_queue, live_settings))
    process.start()

    return lambda event: events_queue.put(event)


def is_available(live_settings):
    session = create_session(live_settings["username"], live_settings["password"])
    url = f"{live_settings['url']}{live_settings['rest_input']}"

    if ("url" in live_settings) and ("rest_input" in live_settings):
        verify_ssl = live_settings.get("verify_ssl", True)
        ssl_message = f'TLS certificate validation is {verify_ssl and "enabled" or "disabled"}'

        try:
            response = session.get(url, verify=verify_ssl)
            response.raise_for_status()
        except ConnectionError as e:
            is_available = False
            messages = [str(e), ssl_message]
        except RequestException as e:
            is_available = e.response.status_code == 405
            messages = [is_available and f"status={e.response.status_code}" or str(e), ssl_message]
        else:
            is_available = False
            messages = ["No result", ssl_message]
    else:
        is_available = False
        messages = ["Not configured"]

    return is_available, messages
