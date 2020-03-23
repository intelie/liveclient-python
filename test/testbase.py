import sys

sys.path.insert(1, "..")

from datetime import datetime
from live_client.utils.timestamp import get_timestamp


def no_action(*args, **kwargs):
    pass


def raises(exception_cls, f, *args, **kwargs):
    try:
        f(*args, **kwargs)
    except exception_cls:
        return True

    return False


class Collector:
    def __init__(self):
        self.buffer = []

    def collect(self, obj):
        self.buffer.append(obj)

    def __call__(self, obj):
        self.collect(obj)

    def is_empty(self):
        return len(self.buffer) == 0

    def __getitem__(self, key):
        return self.buffer[key]
