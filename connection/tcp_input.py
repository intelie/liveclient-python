# -*- coding: utf-8 -*-
import sys
import socket
import json

from live_client.utils import logging

__all__ = ["send_event"]

REQUIRED_PARAMETERS = ["ip", "port"]


def send_event(event, live_settings=None):
    if live_settings is None:
        live_settings = {}

    ip = live_settings["ip"]
    port = live_settings["port"]

    if not event:
        return

    message = "{}\n".format(json.dumps(event))
    python_version = sys.version_info.major
    if python_version == 3:
        message = bytes(message, "utf-8")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((ip, port))
        sock.sendall(message)
    except socket.error:
        logging.exception("ERROR: Cannot send event, server unavailable")
        logging.exception("Event data: {}".format(message))
    finally:
        sock.close()
