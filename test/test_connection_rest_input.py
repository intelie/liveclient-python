from unittest import mock
import requests

from testbase import *

from live_client.connection import rest_input
from predicates import *
from mocks import *
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
