# -*- coding: utf-8 -*-
import asyncio
import queue
from functools import wraps
from multiprocessing import get_context as get_mp_context

from eliot import start_action
from setproctitle import setproctitle
from aiocometd import Client

from live_client.events.constants import EVENT_TYPE_DESTROY, EVENT_TYPE_EVENT
from live_client.connection.rest_input import create_session
from live_client.utils.network import retry_on_failure, ensure_timeout
from live_client.utils import logging


__all__ = ["on_event", "run", "start", "watch"]


def start(statement, settings, timeout=None, **kwargs):
    """
    Sends the query statement via HTTP and returns the comet channels for grabbing the results
    """

    live_settings = settings["live"]
    live_url = live_settings["url"]
    verify_ssl = live_settings.get("verify_ssl", True)

    if "session" not in settings:
        settings.update(
            session=create_session(live_settings["username"], live_settings["password"])
        )
    session = settings["session"]

    realtime = kwargs.get("realtime", False)
    span = kwargs.get("span", None)
    preload = kwargs.get("preload", False)
    max_retries = kwargs.get("max_retries", 0)

    api_url = f"{live_url}/rest/query"
    query_payload = [
        {
            "provider": "pipes",
            "preload": preload,
            "span": span,
            "follow": realtime,
            "expression": statement,
        }
    ]

    with retry_on_failure(timeout, max_retries=max_retries):
        logging.debug(f"Query '{statement}' started")
        r = session.post(api_url, json=query_payload, verify=verify_ssl)
        r.raise_for_status()

    channels = [item.get("channel") for item in r.json()]

    return channels


async def read_results(url, channels, output_queue):
    """
        Reads the results of the comet websocket containing the query output.
        Runs in the reader process.
    """

    setproctitle("live-client: cometd client for channels {}".format(channels))

    with ensure_timeout(3.05):  # TODO: Put this timeout in a variable
        with start_action(action_type="query.read_results", url=url, channels=channels):
            # connect to the server
            async with Client(url) as client:
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


def watch(url, channels, output_queue):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(read_results(url, channels, output_queue))


# [FIXME]: "timeout" when read in the context of this function can easily be interpreted
# as the timeout for the reader process to stop reading and terminate. This is not the case.
# As documented below timeout relates only to one of the steps even before spawning the
# worker process. [ECS]: We should either rename the variable (but do we really need the current
# timeout as it is?), or think about adapting the implementation to something more inline with
# the expected effects.
def run(statement, settings, timeout=None, **kwargs):
    """
        Reads the query results in a separate process (the reader process) and
    reports the results via a queue. Results are put in the queue as they are
    made available. Consumers can then get from the queue to obtain the results.

    Arguments:
        statement (str): The query to be executed
        settings (dict): Context information regarding Live connection.
        timeout (number): Seconds for each retry when requesting the comet channels.
            The total timeout can be up to "timeout * (kwargs['max_retries'] + 1)"
    Returns:
        The results retrieving process and its output queue.
    """

    mp = get_mp_context("fork")

    with start_action(action_type="query.run", statement=statement):
        channels = start(statement, settings, timeout=timeout, **kwargs)
        logging.debug(f"Results channel is {channels}")

        live_settings = settings["live"]
        live_url = live_settings["url"]
        results_url = f"{live_url}/cometd"

        events_queue = mp.Queue()
        process = mp.Process(target=watch, args=(results_url, channels, events_queue))
        process.start()

    return process, events_queue


# [ECS]: The function of this decorator is:
#   1 - Start the query process and
#   2 - Provide a consumer loop for the query results
# The name 'on_event' is a bit misleading as it suggests it would be or create some kind
# of callback for the query results which it is not really.
# Maybe 'run_query' is a better name? Other options: 'query_event_loop', 'event_loop'
def on_event(statement, settings, realtime=True, timeout=None, **query_args):
    def handler_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            results_process, results_queue = run(
                statement, settings, realtime=realtime, timeout=timeout, **query_args
            )
            last_result = None

            while True:
                try:
                    event = results_queue.get(timeout=timeout)
                except queue.Empty:
                    logging.exception(f"No results after {timeout} seconds")
                    break

                event_type = event.get("data", {}).get("type")
                if event_type == EVENT_TYPE_DESTROY:
                    break
                elif event_type != EVENT_TYPE_EVENT:
                    continue

                last_result = f(event, *args, **kwargs)

            # Release resources after the query ends
            results_queue.close()
            results_process.terminate()
            results_process.join()

            return last_result

        return wrapper

    return handler_decorator
