# -*- coding: utf-8 -*-
from functools import partial
from requests.exceptions import RequestException

from eliot import start_action

from live_client.connection.rest_input import build_session
from live_client.utils.network import retry_on_failure
from live_client.utils import logging

__all__ = ["make_request", "request_with_timeout"]


def make_request(url, settings, timeout=None, max_retries=0, handle_errors=True):
    live_settings = settings["live"]
    verify_ssl = live_settings.get("verify_ssl", True)

    if "session" not in live_settings:
        live_settings.update(session=build_session(live_settings))

    session = live_settings["session"]

    with start_action(action_type="make request", url=url):
        with retry_on_failure(timeout, max_retries=max_retries):
            try:
                response = session.get(url, verify=verify_ssl)
                response.raise_for_status()
                content_type = response.headers.get("Content-Type")

                if "text/plain" in content_type:
                    result = response.text
                else:
                    result = response.json()

            except RequestException as e:
                if handle_errors:
                    logging.exception(f"Error during request for {url}, {e}<{type(e)}>")
                    result = None
                else:
                    raise

    return result


request_with_timeout = partial(make_request, timeout=(3.05, 5), max_retries=5)
