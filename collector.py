# -*- coding: utf-8 -*-
import logging
import socket
import json

__all__ = ['send_event']


def send_event(event, output_settings):
    ip = output_settings['ip']
    port = output_settings['port']

    if not event:
        return

    message = '{}\n'.format(
        json.dumps(event)
    )
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((ip, port))
        sock.sendall(message)
    except socket.error:
        logging.exception("ERROR: Cannot send event, server unavailable")
        logging.exception("Event data: {}".format(message))
    finally:
        sock.close()
