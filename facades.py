#from eliot import start_action, preserve_context, Action
import eliot
from functools import partial

from . import query
from .events import messenger, annotation, raw
from .events.constants import EVENT_TYPE_EVENT
from .types.message import Message
from .utils.timestamp import get_timestamp
from .utils import logging


DEFAULT_REQUEST_TIMEOUT = (3.05, 5)
DEFAULT_MAX_RETRIES = 5

def merge_extra_settings(func):
    def ret(*args, **kwargs):
        extra_settings = kwargs.pop("extra_settings", {})
        if extra_settings:
            process_settings = kwargs.get("process_settings", {})
            process_settings.update(extra_settings)
            kwargs["process_settings"] = process_settings
        return func(*args, **kwargs)
    return ret


@eliot.preserve_context
@merge_extra_settings
def send_message(*args, **kwargs):
    return messenger.send_message(*args, **kwargs)


class LiveClient:
    def __init__(self, process_name, process_settings, output_info, room_id):
        self.process_name = process_name
        self.process_settings = process_settings
        self.output_info = output_info
        self.room_id = room_id

        #self.annotate = partial(
        #    create_annotation,
        #    process_settings=process_settings,
        #    output_info=output_info,
        #    room={"id": room_id},
        #)

        #self.send_event = partial(
        #    send_event, process_settings=process_settings, output_info=output_info
        #)

    def run_query(self, query_str, realtime, span=None):
        run_query = partial(
            query.run,
            self.process_name,
            self.process_settings,
            timeout = DEFAULT_REQUEST_TIMEOUT,
            max_retries = DEFAULT_MAX_RETRIES,
        )
        return run_query(query_str, realtime = realtime, span = span)

    def send_message(self, message):
        send = partial(
            send_message,
            self.process_name,
            process_settings=self.process_settings,
            output_info=self.output_info,
            room={"id": self.room_id},
        )
        return send(message, get_timestamp())
