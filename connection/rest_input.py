# -*- coding: utf-8 -*-
import logging
import requests
from requests.exceptions import RequestException

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
