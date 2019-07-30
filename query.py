# -*- coding: utf-8 -*-
import asyncio
import requests
from setproctitle import setproctitle

from aiocometd import Client


HOST = 'https://shellgamechanger.intelie.com'
USERNAME = 'live-agent'
PASSWORD = 'tEqwGSQb'


def start(host, username, password, statement, realtime=False, span=None):
    session = requests.Session()
    session.auth = (username, password)

    api_url = '{}/rest/query'.format(host)
    query_payload = [{
        'provider': 'pipes',
        'preload': False,
        'span': span,
        'follow': realtime,
        'expression': statement
    }]

    r = session.post(api_url, json=query_payload)
    r.raise_for_status()

    channels = [
        item.get('channel')
        for item in r.json()
    ]

    return channels


async def read_results(url, channels, output_queue):
    setproctitle('DDA: cometd client for channels {}'.format(channels))

    # connect to the server
    async with Client(url) as client:

            # subscribe to channels to receive chat messages and
            # notifications about new members
            for channel in channels:
                await client.subscribe(channel)

            # listen for incoming messages
            async for message in client:
                output_queue.put(message)


def watch(url, channels, output_queue):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(read_results(url, channels, output_queue))
