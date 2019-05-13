# -*- coding: utf-8
from . import (
    collector,
    rest_input
)

__all__ = ['CONNECTION_HANDLERS']

CONNECTION_HANDLERS = {
    'tcp': collector.send_event,
    'rest': rest_input.send_event,
}
