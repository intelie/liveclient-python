# -*- coding: utf-8 -*-
from functools import partial
from requests.exceptions import RequestException

from eliot import start_action

from live_client.connection.rest_input import build_session
from live_client.utils.network import retry_on_failure
from live_client.utils import logging

__all__ = ["make_request", "request_with_timeout"]


def make_request(url, settings, timeout=None, max_retries=0):
    live_settings = settings["live"]

    if "session" not in live_settings:
        live_settings.update(session=build_session(live_settings))

    session = live_settings["session"]

    with start_action(action_type="make request", url=url):
        with retry_on_failure(timeout, max_retries=max_retries):
            try:
                response = session.get(url)
                response.raise_for_status()
                result = response.json()

            except RequestException as e:
                logging.exception(f"Error during request for {url}, {e}<{type(e)}>")
                result = None

    return result


request_with_timeout = partial(make_request, timeout=(3.05, 5), max_retries=5)
