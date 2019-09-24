# -*- coding: utf-8 -*-
from requests.exceptions import RequestException

from eliot import start_action

from live_client.connection.rest_input import build_session
from live_client.utils.network import retry_on_failure
from live_client.utils import logging

__all__ = [
    'make_request',
    'only_enabled_curves',
]


def make_request(process_name, process_settings, output_info, url, timeout=None, max_retries=0):
    connection_func, output_settings = output_info
    live_settings = process_settings['live']

    if 'session' not in output_settings:
        output_settings.update(
            session=build_session(live_settings)
        )

    session = output_settings['session']

    with start_action(action_type=u"make request", url=url):
        with retry_on_failure(timeout, max_retries=max_retries):
            try:
                response = session.get(url)
                response.raise_for_status()
                result = response.json()

            except RequestException as e:
                logging.exception(f"Error during request for {url}, {e}<{type(e)}>")
                result = None

    return result


def only_enabled_curves(curves):
    idle_curve = [{}]

    return dict(
        (name, value) for (name, value) in curves.items()
        if value.get('options', idle_curve) != idle_curve
    )
