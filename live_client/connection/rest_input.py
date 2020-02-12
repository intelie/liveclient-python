# -*- coding: utf-8 -*-
import requests
from multiprocessing import Process, Queue

from requests.exceptions import RequestException
from setproctitle import setproctitle
from eliot import start_action

from live_client.utils import logging
from live_client.utils.network import retry_on_failure

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
    url = f"{live_settings['url']}{live_settings['rest_input']}"

    if not event:
        return

    try:
        with retry_on_failure(3.05, max_retries=5):
            response = session.post(url, json=event)
            response.raise_for_status()
    except RequestException as e:
        logging.exception("ERROR: Cannot send event, {}<{}>".format(e, type(e)))
        logging.exception("Event data: {}".format(event))


def async_send(queue, live_settings):
    with start_action(action_type="async_logger"):
        logging.info("Remote logger process started")
        setproctitle("DDA: Remote logger")

        live_settings.update(session=build_session(live_settings))
        while True:
            event = queue.get()
            send_event(event, live_settings)


def async_event_sender(live_settings):
    events_queue = Queue()
    process = Process(target=async_send, args=(events_queue, live_settings))
    process.start()

    return lambda event: events_queue.put(event)
