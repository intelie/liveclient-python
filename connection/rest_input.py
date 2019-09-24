# -*- coding: utf-8 -*-
import requests
from multiprocessing import Process, Queue

from requests.exceptions import RequestException
from setproctitle import setproctitle
from eliot import start_action

from live_client.utils import logging

__all__ = ['send_event']


def build_session(output_settings):
    username = output_settings['username']
    password = output_settings['password']

    session = requests.Session()
    session.auth = (username, password)

    return session


def send_event(event, output_settings):
    if 'session' not in output_settings:
        output_settings.update(
            session=build_session(output_settings)
        )

    session = output_settings['session']
    url = output_settings['url']

    if not event:
        return

    try:
        response = session.post(url, json=event)
        response.raise_for_status()
    except RequestException as e:
        logging.exception("ERROR: Cannot send event, {}<{}>".format(e, type(e)))
        logging.exception("Event data: {}".format(event))


def async_send(queue, output_settings):
    with start_action(action_type='async_logger'):
        logging.info("Remote logger process started")
        setproctitle('DDA: Remote logger')

        output_settings.update(
            session=build_session(output_settings)
        )
        while True:
            event = queue.get()
            send_event(event, output_settings)


def async_event_sender(output_settings):
    events_queue = Queue()
    process = Process(
        target=async_send,
        args=(events_queue, output_settings)
    )
    process.start()

    return lambda event: events_queue.put(event)
