# -*- coding: utf-8 -*-
import asyncio
from multiprocessing import Process, Queue
from requests.exceptions import Timeout

from eliot import start_action, preserve_context
from setproctitle import setproctitle

from aiocometd import Client

from live_client.events.constants import EVENT_TYPE_DESTROY
from live_client.connection.rest_input import build_session
from live_client.utils import logging


__all__ = [
    'run',
    'start',
    'watch',
]


def start(process_settings, statement, realtime=False, span=None, timeout=None, retry=False):
    live_settings = process_settings['live']

    if 'session' not in process_settings:
        process_settings.update(
            session=build_session(live_settings)
        )

    host = live_settings['host']
    session = process_settings['session']

    api_url = f'{host}/rest/query'
    query_payload = [{
        'provider': 'pipes',
        'preload': False,
        'span': span,
        'follow': realtime,
        'expression': statement
    }]

    request_finished = False
    retries = 0
    max_retries = 5

    while request_finished is False:
        try:
            logging.debug(f"Query '{statement}' started")
            r = session.post(api_url, json=query_payload)
            r.raise_for_status()
        except Timeout:
            if retry is True and (retries < max_retries):
                logging.info(f"Query timed out, retrying ({retries}/{max_retries})")
                retries += 1
                continue

            logging.error(f"Query timed out")

        request_finished = True

    channels = [
        item.get('channel')
        for item in r.json()
    ]

    return channels


async def read_results(url, channels, output_queue):
    setproctitle('DDA: cometd client for channels {}'.format(channels))

    with start_action(action_type=u"query.read_results", url=url, channels=channels):
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
                event_data = message.get('data', {})
                event_type = event_data.get('type')
                if event_type == EVENT_TYPE_DESTROY:
                    return


def watch(url, channels, output_queue):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(read_results(url, channels, output_queue))


@preserve_context
def run(process_name, process_settings, statement, realtime=False, span=None, timeout=None, retry=False):  # NOQA
    with start_action(action_type=u"query.run", statement=statement):
        live_settings = process_settings['live']
        host = live_settings['host']

        channels = start(
            process_settings,
            statement,
            realtime=realtime,
            span=span,
            timeout=timeout,
            retry=retry
        )

        logging.debug(f"Results channel is {channels}")

        host = live_settings['host']
        results_url = '{}/cometd'.format(host)

        events_queue = Queue()
        process = Process(
            target=watch,
            args=(results_url, channels, events_queue),
        )
        process.start()

    return process, events_queue
