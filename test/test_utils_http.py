from testbase import *
import copy
import json
import multiprocessing as mp
import pytest
import requests

from unittest import mock

from live_client.utils import http
from mocks import *
from predicates import *
from utils import vcrutils


DEFAULT_SETTINGS = {
    "live": {
        "username": "",
        "password": "",
        "url": "http://localhost:8080",
        "rest_input": "/services/plugin-restinput/DDA/",
        "user_id": 1,
    }
}


def _build_default_settings():
    return copy.deepcopy(DEFAULT_SETTINGS)


class TestMakeRequest:
    def test_raises_on_invalid_settings(self):
        settings = _build_default_settings()
        with pytest.raises(KeyError):
            channels = http.make_request("_", {})

        with pytest.raises(KeyError):
            channels = http.make_request("_", {"live": {}})

    def test_fails_on_invalid_url(self):
        settings = _build_default_settings()

        url = ""  # --> RequestException (Missing Schema)
        result = http.make_request(url, settings)
        assert result == None

        url = "http://invalid.inv"  # --> RequestException (Connection Error)
        result = http.make_request(url, settings)
        assert result == None

        url = ""  # --> RequestException (Missing Schema)
        with pytest.raises(requests.exceptions.RequestException):
            result = http.make_request(url, settings, None, False)

        url = "http://invalid.inv"  # --> RequestException (Connection Error)
        with pytest.raises(requests.exceptions.RequestException):
            result = http.make_request(url, settings, None, False)

    @vcrutils.use_safe_cassete("test_utils_http_make_request_plain.yml")
    def test_successful_request_plain(self):
        settings = _build_default_settings()
        url = "http://localhost:8080"

        response = http.make_request(url, settings)
        assert type(response) is str

    @vcrutils.use_safe_cassete("test_utils_http_make_request_json.yml")
    def test_successful_request_json(self):
        settings = _build_default_settings()
        # TODO: Change this url to something local
        url = "https://api.lyrics.ovh/v1/Seal/Crazy"

        response = http.make_request(url, settings)
        assert type(response) is dict
