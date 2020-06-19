# -*- coding: utf-8 -*-
import requests
from multiprocessing import get_context as get_mp_context

from requests.exceptions import RequestException, ConnectionError
from setproctitle import setproctitle
from eliot import start_action

from live_client.utils import logging
from live_client.utils.network import retry_on_failure
from live_client.utils.processes import get_start_method

__all__ = ["send_event"]

REQUIRED_PARAMETERS = ["url", "username", "password", "rest_input"]


def build_session(live_settings):
    username = live_settings["username"]
    password = live_settings["password"]

    session = requests.Session()
    session.auth = (username, password)

    return session


def send_event(event, live_settings=None):
    if live_settings is None:
        live_settings = {}

    if "session" not in live_settings:
        live_settings.update(session=build_session(live_settings))

    session = live_settings["session"]
    verify_ssl = live_settings.get("verify_ssl", True)
    url = f"{live_settings['url']}{live_settings['rest_input']}"

    if not event:
        return

    try:
        with retry_on_failure(3.05, max_retries=5):
            response = session.post(url, json=event, verify=verify_ssl)
            response.raise_for_status()
    except RequestException as e:
        logging.exception("ERROR: Cannot send event, {}<{}>".format(e, type(e)))
        logging.exception("Event data: {}".format(event))
        raise


def async_send(queue, live_settings):
    with start_action(action_type="async_logger"):
        logging.info("Remote logger process started")
        setproctitle("DDA: Remote logger")

        live_settings.update(session=build_session(live_settings))
        while True:
            event = queue.get()
            try:
                send_event(event, live_settings)
            except RequestException:
                logging.warn("Ignoring previous exception")
                pass


def async_event_sender(live_settings):
    mp = get_mp_context(get_start_method())
    events_queue = mp.Queue()
    process = mp.Process(target=async_send, args=(events_queue, live_settings))
    process.start()

    return lambda event: events_queue.put(event)


def is_available(live_settings):
    session = build_session(live_settings)
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
