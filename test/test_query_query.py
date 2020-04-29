from testbase import *

import asyncio
import copy
import queue
import re
from unittest import mock

import json
import multiprocessing as mp
import pytest
import requests
import time

from live_client import events
from live_client.query import query
from mocks import *
from predicates import *
from utils import vcrutils


DEFAULT_SETTINGS = {
    "live": {
        "username": "admin",
        "password": "admin",
        "url": "http://localhost:8080",
        "rest_input": "/services/plugin-restinput/DDA/",
        "user_id": 1,
    },
    "output": {
        "author": {"id": 1, "name": "🤖  Test Script"},
        "room": {"id": "7g61s2lch7h081e05e1cs3m5cq"},
    },
}


def _build_default_settings():
    return copy.deepcopy(DEFAULT_SETTINGS)


class TestQueryStart:
    @vcrutils.use_safe_cassete("test_query_query_start.yml")
    def test_returns_channels_on_good_data(self):
        settings = _build_default_settings()
        query_str = "__message message:__teste__"
        channels = query.start(query_str, settings)
        assert len(channels) > 0
        for channel in channels:
            m = re.match(r"/data/[0-9a-fA-F]{32}", channel)
            assert m is not None

    @vcrutils.use_safe_cassete("test_query_query_start_02.yml")
    def test_raises_if_invalid_url(self):
        settings = _build_default_settings()
        query_str = "__message message:__teste__"

        settings["live"]["url"] = ""  # --> RequestException (Missing Schema)
        with pytest.raises(requests.exceptions.RequestException):
            channels = query.start(query_str, settings)

        settings["live"]["url"] = "http://invalid.inv"  # --> RequestException (Connection Error)
        with pytest.raises(requests.exceptions.RequestException):
            channels = query.start(query_str, settings)

    def test_raises_on_invalid_settings(self):
        settings = _build_default_settings()
        with pytest.raises(KeyError):
            channels = query.start("_", {})

        with pytest.raises(KeyError):
            channels = query.start("_", {"live": {}})


class TestQueryRun:
    def test_raises_on_invalid_settings(self):
        settings = _build_default_settings()
        with pytest.raises(KeyError):
            channels = query.run("_", {})

        with pytest.raises(KeyError):
            channels = query.run("_", {"live": {}})

    @vcrutils.use_safe_cassete("test_query_query_run.yml")
    def test_returns_process_and_queue_on_valid_data(self):
        settings = _build_default_settings()

        query_str = "__message message:__teste__"
        process, queue = query.run(query_str, settings)
        assert isinstance(process, mp.context.ForkContext.Process)
        assert process.is_alive()
        assert isinstance(queue, mp.queues.Queue)

        queue.close()
        process.terminate()
        process.join()

    @mock.patch("multiprocessing.context.ForkContext.Process")
    @vcrutils.use_safe_cassete("test_query_query_run.yml")
    def test_process_created_with_proper_arguments(self, mock_Process):
        settings = _build_default_settings()
        query_str = "_"
        process, queue = query.run(query_str, settings, realtime=True)

        args = mock_Process.call_args[1].get("args")
        assert args[0].endswith("/cometd")
        assert all(map(lambda s: s.startswith("/data"), args[1]))
        assert isinstance(args[2], mp.queues.Queue)


class TestOnEvent:
    def test_decorated_function_has_correct_name(self):
        @query.on_event("", {})
        def fn_test(event):
            print(event)

        assert fn_test.__name__ == "fn_test"

    @mock.patch("live_client.query.query.run")
    def test_starts_the_query_process(self, mock_run):
        output_queue = MPQueue()
        mock_process = mock.Mock()
        mock_run.return_value = (mock_process, output_queue)

        # fmt:off
        event = {
            "data": {
                "type": events.constants.EVENT_TYPE_DESTROY
            }
        }
        # fmt:on
        output_queue.put(event)

        @query.on_event("", {})
        def fn_test(event):
            print(event)

        fn_test()

        assert mock_run.called

    @mock.patch("live_client.query.query.run")
    def test_tries_to_get_results(self, mock_run):
        # fmt:off
        event = {
            "data": {
                "type": events.constants.EVENT_TYPE_DESTROY
            }
        }
        # fmt:on
        mock_queue = mock.Mock()
        mock_queue.get = mock.Mock()
        mock_queue.get.return_value = event
        mock_process = mock.Mock()
        mock_run.return_value = (mock_process, mock_queue)

        @query.on_event("", {})
        def fn_test(event):
            pass

        fn_test()

        assert mock_queue.get.called

    @mock.patch("live_client.query.query.run")
    def test_performs_cleanup(self, mock_run):
        # fmt:off
        event = {
            "data": {
                "type": events.constants.EVENT_TYPE_DESTROY
            }
        }
        # fmt:on

        mock_queue = mock.Mock()
        mock_queue.get = mock.Mock()
        mock_queue.get.return_value = event
        mock_process = mock.Mock()
        mock_run.return_value = (mock_process, mock_queue)

        @query.on_event("", {})
        def fn_test(event):
            pass

        fn_test()

        assert mock_queue.close.called
        assert mock_process.terminate.called
        assert mock_process.join.called
