from testbase import *

import copy
import pytest
import requests

from unittest import mock

from live_client.resources import dashboards
from mocks import *
from predicates import *
from utils import vcrutils

# fmt:off
DEFAULT_SETTINGS = {
    "live": {
        "username": "admin",
        "password": "admin",
        "url": "http://localhost:8080",
    }
}
# fmt:off


def _build_default_settings():
    return copy.deepcopy(DEFAULT_SETTINGS)


class TestListDashboards:
    @mock.patch("live_client.resources.base.fetch_resource")
    def test_calls_the_correct_endpoint(self, mock_fetch_resource):
        settings = _build_default_settings()
        dashboards.list_dashboards(settings)
        assert mock_fetch_resource.called_with("/rest/dashboard", settings)
