# -*- coding: utf-8
from . import tcp_input, rest_input

__all__ = ["CONNECTION_HANDLERS"]

CONNECTION_HANDLERS = {"tcp": tcp_input.send_event, "rest": rest_input.send_event}
