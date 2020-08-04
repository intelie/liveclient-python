# -*- coding: utf-8 -*-
import asyncio
import queue
from multiprocessing import get_context as get_mp_context

from eliot import start_action
from setproctitle import setproctitle
from aiocometd import Client, ConnectionType

from live_client.events.constants import EVENT_TYPE_DESTROY, EVENT_TYPE_EVENT, EVENT_TYPE_SPAN
from live_client.connection.rest_input import build_session
from live_client.utils.network import retry_on_failure, ensure_timeout
from live_client.utils.processes import get_start_method
from live_client.utils import logging


__all__ = ["on_event", "run", "start", "watch"]


def start(statement, settings, timeout=None, **kwargs):
    live_settings = settings["live"]
    live_url = live_settings["url"]
    verify_ssl = live_settings.get("verify_ssl", True)

    if "session" not in settings:
        settings.update(session=build_session(live_settings))
    session = settings["session"]

    max_retries = kwargs.get("max_retries", 0)

    api_url = f"{live_url}/rest/query"
    query_payload = [
        {
            "provider": kwargs.get("provider", "pipes"),
            "reducer": kwargs.get("reducer", None),
            "preload": kwargs.get("preload", True),
            "span": kwargs.get("span", None),
            "follow": kwargs.get("realtime", False),
            "expression": statement,
        }
    ]

    with retry_on_failure(timeout, max_retries=max_retries):
        logging.debug(f"Query '{statement}' started")
        r = session.post(api_url, json=query_payload, verify=verify_ssl)
        r.raise_for_status()

    channels = [item.get("channel") for item in r.json()]

    return channels


async def read_results(url, channels, output_queue, settings):
    setproctitle("live-client: cometd client for channels {}".format(channels))
    live_settings = settings["live"]
    verify_ssl = live_settings.get("verify_ssl", None)
    connection_types = settings.get(
        "connection_type", [ConnectionType.LONG_POLLING, ConnectionType.WEBSOCKET]
    )

    with ensure_timeout(3.05):
        with start_action(action_type="query.read_results", url=url, channels=channels):
            # connect to the server
            async with Client(url, ssl=verify_ssl, connection_types=connection_types) as client:
                for channel in channels:
                    logging.debug(f"Subscribing to '{channel}'")
                    await client.subscribe(channel)

                # listen for incoming messages
                async for message in client:
                    logging.debug(f"New message'{message}'")
                    output_queue.put(message)

                    # Exit after the query has stopped
                    event_data = message.get("data", {})
                    event_type = event_data.get("type")
                    if event_type == EVENT_TYPE_DESTROY:
                        return


def watch(url, channels, output_queue, settings):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(read_results(url, channels, output_queue, settings))


def run(statement, settings, timeout=None, **kwargs):
    mp = get_mp_context(get_start_method())

    with start_action(action_type="query.run", statement=statement):
        live_settings = settings["live"]

        channels = start(statement, settings, timeout=timeout, **kwargs)

        logging.debug(f"Results channel is {channels}")

        live_url = live_settings["url"]
        results_url = f"{live_url}/cometd"

        events_queue = mp.Queue()
        process = mp.Process(target=watch, args=(results_url, channels, events_queue, settings))
        process.start()

    return process, events_queue


def on_event(statement, settings, realtime=True, timeout=None, **query_args):
    def handler_decorator(f):
        def wrapper(*args, **kwargs):
            results_process, results_queue = run(
                statement, settings, realtime=realtime, timeout=timeout, **query_args
            )
            last_result = None

            while True:
                try:
                    event = results_queue.get(timeout=timeout)
                    event_type = event.get("data", {}).get("type")
                    if event_type == EVENT_TYPE_EVENT:
                        last_result = f(event, *args, **kwargs)
                    elif event_type == EVENT_TYPE_DESTROY:
                        break
                    else:
                        if event_type != EVENT_TYPE_SPAN:
                            logging.info(f"Got event with type={event_type}")

                        continue
                except queue.Empty:
                    logging.exception(f"No results after {timeout} seconds")
                    break
                except EOFError as e:
                    logging.exception(f"Connection lost: {e}")
                    break

            # Release resources after the query ends
            results_queue.close()
            results_process.terminate()
            results_process.join()

            return last_result

        return wrapper

    return handler_decorator
