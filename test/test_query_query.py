from testbase import *

import re
from unittest import mock

import json
import multiprocessing as mp
import pytest
import requests
import time
import vcr

from live_client.query import query
from mocks import *
from predicates import *
from utils import settings as S

_vcr = vcr.VCR(cassette_library_dir='fixtures/cassettes')


settings = {
    "live": {
        "username": 'admin',
        "password": 'admin',
        "url": "http://localhost:8080",
        "rest_input": '/services/plugin-restinput/DDA/',
        "user_id": 1,
    },
    "output": {
        "author": {"id": 1, "name": "🤖  Test Script"},
        "room": {"id": "7g61s2lch7h081e05e1cs3m5cq"},
    },
}


def _use_safe_cassete(*args, **kwargs):
    """
    Builds a cassette without sensitive data so we can store it
    """
    required_header_filters = ["authorization"]
    filter_headers = kwargs.get("filter_headers", [])
    for header in required_header_filters:
        if not header in filter_headers:
            filter_headers.append(header)
    kwargs["filter_headers"] = filter_headers

    def before_record_response(original_response):
        original_response['headers']['Set-Cookie'] = ""
        return original_response
    kwargs["before_record_response"] = before_record_response

    return _vcr.use_cassette(*args, **kwargs)


class TestQueryStart:
    @_use_safe_cassete("test_query_query_start.yml", record_mode="new_episodes")
    def test_returns_channels_on_good_data(self):
        query_str = "__message message:__teste__"
        channels = query.start(query_str, settings)
        assert len(channels) > 0
        for channel in channels:
            m = re.match(r"/data/[0-9a-fA-F]{32}", channel)
            assert m is not None

    @_use_safe_cassete("test_query_query_start.yml", record_mode="new_episodes")
    def test_raises_if_invalid_url(self):
        query_str = "__message message:__teste__"

        settings["live"]["url"] = "" # --> RequestException (Missing Schema)
        with pytest.raises(requests.exceptions.RequestException):
            channels = query.start(query_str, settings)

        settings["live"]["url"] = "http://invalid.inv" # --> RequestException (Connection Error)
        with pytest.raises(requests.exceptions.RequestException):
            channels = query.start(query_str, settings)

    def test_raises_on_invalid_settings(self):
        with pytest.raises(KeyError):
            channels = query.start("_", {})

        with pytest.raises(KeyError):
            channels = query.start("_", {"live": {}})