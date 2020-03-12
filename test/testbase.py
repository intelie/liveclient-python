import sys

sys.path.insert(1, "..")

from datetime import datetime


def now_timestamp():
    return int(datetime.now().timestamp() * 1000)


def no_action(*args, **kwargs):
    pass


def raises(exception_cls, f, *args, **kwargs):
    try:
        f(*args, **kwargs)
    except exception_cls:
        return True

    return False


class Collector:
    buffer = []

    def collect(self, obj):
        self.buffer.append(obj)

    def __call__(self, obj):
        self.collect(obj)
