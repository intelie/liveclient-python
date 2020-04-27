from testbase import *

import time
from unittest import mock

from live_client.utils import timestamp as TS
from mocks import *
from predicates import *


class TestGetTimestamp:
    def test_timestamp_is_integer(self):
        ts = TS.get_timestamp()
        assert type(ts) is int

    def test_last_timestamp_is_higher_than_previous(self):
        ts1 = TS.get_timestamp()
        time.sleep(0.01)
        ts2 = TS.get_timestamp()
        assert ts2 > ts1
