from testbase import *

import json
import multiprocessing as mp
import queue
import requests
import time

from unittest import mock

from live_client.connection import rest_input
from mocks import *
from predicates import *
from utils import settings as S

DEFAULT_SETTINGS = {param: "" for param in rest_input.REQUIRED_PARAMETERS}


class TestSendEvent:
    def test_returns_false_if_no_or_empty_event(self):
        assert rest_input.send_event(None, {}) == False
        assert rest_input.send_event({}, {}) == False

    def test_raises_if_no_settings(self):
        assert raises(Exception, rest_input.send_event, {"message": "_"}, None)

    def test_raises_on_invalid_settings(self):
        assert raises(
            Exception,
            rest_input.send_event,
            {"message": "_"},
            {"url": "", "username": "", "password": ""},
        )
        assert raises(
            Exception,
            rest_input.send_event,
            {"message": "_"},
            {"url": "", "username": "", "rest_input": ""},
        )
        assert raises(
            Exception,
            rest_input.send_event,
            {"message": "_"},
            {"url": "", "password": "", "rest_input": ""},
        )
        assert raises(
            Exception,
            rest_input.send_event,
            {"message": "_"},
            {"username": "", "password": "", "rest_input": ""},
        )

    @mock.patch("requests.Session.post")
    @mock.patch("requests.Response.raise_for_status")
    def test_attempts_to_send_event_if_valid_data(self, raise_for_status_mock, post_mock):
        res = rest_input.send_event({"message": "_"}, DEFAULT_SETTINGS)
        assert res == True

    @mock.patch("requests.Session.post")
    @mock.patch("requests.Response.raise_for_status")
    def test_updates_the_session_on_success(self, raise_for_status_mock, post_mock):
        DEFAULT_SETTINGS["session"] = None
        res = rest_input.send_event({"message": "_"}, DEFAULT_SETTINGS)
        assert DEFAULT_SETTINGS.get("session") is not None


class TestAsyncSend:
    @mock.patch("requests.Session.post")
    def test_event_trigered_on_queue_put(self, post_mock):
        q = queue.Queue()
        event = {"message": "teste !"}
        q.put(event)
        q.put(None)
        rest_input.async_send(q, DEFAULT_SETTINGS)
        post_mock.assert_called_with(
            DEFAULT_SETTINGS["url"] + DEFAULT_SETTINGS["rest_input"], json=event, verify=True
        )


# class TestAsyncEventSender:
#    pass


class TestIsAvailable:
    @mock.patch("requests.Session.get")
    def test_shall_return_status_and_messages(self, get_mock):
        result = rest_input.is_available(DEFAULT_SETTINGS)
        assert type(result[0]) == bool
        assert type(result[1]) == list
        for val in result[1]:
            assert type(val) == str

    @mock.patch("requests.Session.get")
    def test_shall_notify_wrong_configuration(self, get_mock):
        settings = {}
        result = rest_input.is_available(settings)

        assert result[0] == False
        assert result[1][0] == "Not configured"

    @mock.patch("requests.Session.get")
    def test_shall_return_true_on_method_not_allowed(self, get_mock):
        response = mock.Mock()
        response.status_code = 405
        get_mock.side_effect = requests.exceptions.RequestException(response=response)
        result = rest_input.is_available(DEFAULT_SETTINGS)

        assert result[0] == True
        assert result[1][0] == f"status={response.status_code}"

    @mock.patch("requests.Session.get")
    def test_request_is_called_with_ssl_disabled(self, get_mock):
        settings = DEFAULT_SETTINGS.copy()
        settings["verify_ssl"] = False
        result = rest_input.is_available(settings)
        assert get_mock.call_args[1].get("verify") == settings["verify_ssl"]
