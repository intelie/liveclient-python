# -*- coding: utf-8 -*-
import socket
import threading
from contextlib import contextmanager

from requests.exceptions import Timeout

from live_client.utils import logging

__all__ = ["ensure_timeout"]


class Context:
    def __init__(self, default_timeout):
        self.default_timeout = default_timeout


# fmt:off
_default_context = Context(
    default_timeout=3.05,
)
# fmt:off
_local = threading.local()


def getcontext(local=_local):
    try:
        return local.__network_context__
    except AttributeError:
        # Multiple contexts are not supported now, so we just return the one we have
        local.__network_context__ = _default_context
        return local.__network_context__

del _local


@contextmanager
def ensure_timeout(timeout):
    default_timeout = socket.getdefaulttimeout()
    if isinstance(timeout, (list, tuple)):
        socket_timeout = timeout[0]
    else:
        socket_timeout = timeout

    if socket_timeout is not None:
        socket.setdefaulttimeout(socket_timeout)

    logging.debug(f"Socket timeout is now {socket_timeout}")

    try:
        yield
    finally:
        socket.setdefaulttimeout(default_timeout)
        logging.debug(f"Socket timeout back to default ({default_timeout})")
