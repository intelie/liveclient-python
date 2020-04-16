from testbase import *

import json
import multiprocessing as mp
import queue
import requests
import time

from unittest import mock

from live_client.connection import autodetect, rest_input, tcp_input
from mocks import *
from predicates import *
from utils import settings as S

TCP_SETTINGS = {"ip": "127.0.0.1", "port": 3210}
REST_SETTINGS = {
    "url": "",
    "username": "",
    "password": "",
    "rest_input": "",
}


class TestSendEvent:
    @mock.patch("live_client.connection.tcp_input.send_event")
    @mock.patch("live_client.connection.rest_input.send_event")
    def test_rest_function_chosen(self, mock_rest_send_event, mock_tcp_send_event):
        autodetect.send_event({"message": "!_!"}, REST_SETTINGS)
        assert mock_rest_send_event.called
        assert not mock_tcp_send_event.called

    @mock.patch("live_client.connection.tcp_input.send_event")
    @mock.patch("live_client.connection.rest_input.send_event")
    def test_tcp_function_chosen(self, mock_rest_send_event, mock_tcp_send_event):
        autodetect.send_event({"message": "!_!"}, TCP_SETTINGS)
        assert not mock_rest_send_event.called
        assert mock_tcp_send_event.called


class TestBuildSenderFunction:
    def test_send_event_wrapped(self):
        obj = autodetect.build_sender_function(REST_SETTINGS)
        assert obj.func is autodetect.send_event

    def test_is_closure_with_live_settings(self):
        obj = autodetect.build_sender_function(REST_SETTINGS)
        assert obj.keywords["live_settings"] is REST_SETTINGS


class TestHasRequiredKeys:
    required_keys = ["a", "b"]

    def test_returns_true_if_keys_match(self):
        container = {"a": 1, "b": 2}
        assert autodetect.has_required_keys(container, self.required_keys) == True

    def test_returns_true_if_keys_exceed(self):
        container = {"a": 1, "b": 2, "c": 3}
        assert autodetect.has_required_keys(container, self.required_keys) == True

    def test_returns_true_if_no_required_key(self):
        container = {"a": 1, "b": 2, "c": 3}
        assert autodetect.has_required_keys(container, []) == True

    def test_returns_false_on_missing_key(self):
        container = {"a": 1, "c": "3"}
        assert autodetect.has_required_keys(container, self.required_keys) == False
