from testbase import *

import socket
import time
from unittest import mock

from mocks import *
from predicates import *

# WORKAROUND !! This import is not necessary. It is here only to avoid problems
# with circular imports envolving (utils.network, utils.logging and rest_input)
# FIXME
from live_client.connection import rest_input

from live_client.utils import network


class TestEnsureTimeout:
    def test_new_timeout_is_applied(self):
        current_timeout = socket.getdefaulttimeout()
        new_timeout = 1.11
        assert current_timeout is None or not float_equals(current_timeout, new_timeout)
        with network.ensure_timeout(new_timeout):
            timeout = socket.getdefaulttimeout()
            assert float_equals(timeout, new_timeout)

    def test_timeout_is_restored(self):
        current_timeout = socket.getdefaulttimeout()
        new_timeout = 1.11
        assert current_timeout is None or not float_equals(current_timeout, new_timeout)
        with network.ensure_timeout(new_timeout):
            pass
        timeout = socket.getdefaulttimeout()
        assert timeout == current_timeout or float_equals(timeout, current_timeout)

    def test_timeout_is_first_element_of_list_or_tuple(self):
        new_timeout = [1.11]
        try:
            with network.ensure_timeout(new_timeout):
                pass
        except:
            assert False

        new_timeout = (1.11,)
        try:
            with network.ensure_timeout(new_timeout):
                pass
        except:
            assert False
