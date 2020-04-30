from testbase import *

import copy
import pytest
import requests

from unittest import mock

from live_client.resources import base
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


class TestFetchResource:
    def test_raises_if_not_handling_errors(self):
        settings = _build_default_settings()
        with pytest.raises(requests.exceptions.RequestException):
            base.fetch_resource("", settings, False)

    def test_returns_none_if_handling_errors(self):
        settings = _build_default_settings()
        base.fetch_resource("", settings, True) == None

    @vcrutils.use_safe_cassete("test_resouces_base_fetch_resource.yml")
    def test_retrieves_resource(self):
        settings = _build_default_settings()
        settings["live"]["username"] = "admin"
        settings["live"]["password"] = "admin"

        resource = base.fetch_resource("/healthcheck", settings)
        assert resource is not None


class TestIsLiveAvailable:
    @vcrutils.use_safe_cassete("test_resouces_base_is_live_available_success_on_avaliable.yml")
    def test_success_on_avaliable(self):
        # fmt:off
        settings = {
            "live": {
                "username": "admin",
                "password": "admin",
                "url": "http://localhost:8080",
            }
        }
        # fmt:on

        assert base.is_live_available(settings)

    @vcrutils.use_safe_cassete("test_resouces_base_is_live_available_fail_on_unavaliable.yml")
    def test_fail_on_unavaliable(self):
        # fmt:off
        settings = {
            "live": {
                "username": "admin",
                "password": "admin",
                "url": "http://localhost:8888",
            }
        }
        # fmt:on

        assert not base.is_live_available(settings)
