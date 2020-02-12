# -*- coding: utf-8 -*-
import socket
from contextlib import contextmanager

from requests.exceptions import Timeout

from live_client.utils import logging

__all__ = ["ensure_timeout"]


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


@contextmanager
def retry_on_failure(timeout=3.05, max_retries=0):
    request_finished = False
    retries = 0

    while request_finished is False:
        try:
            with ensure_timeout(timeout):
                yield
        except (socket.timeout, Timeout):
            if max_retries and (retries < max_retries):
                logging.info(f"Operation timed out, retrying ({retries}/{max_retries})")
                retries += 1
                continue
            else:
                logging.error(f"Operation timed out")
        finally:
            request_finished = True
