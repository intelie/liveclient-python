from . import query
from .events import messenger
from .utils.timestamp import get_timestamp


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


@merge_extra_settings
def send_message(*args, **kwargs):
    return messenger.send_message(*args, **kwargs)


class LiveClient:
    def __init__(self, process_settings, room_id):
        self.process_settings = process_settings
        self.room_id = room_id

    def run_query(self, query_str, realtime, span=None):
        return query.run(
            query_str,
            self.process_settings,
            realtime=realtime,
            span=span,
            timeout=DEFAULT_REQUEST_TIMEOUT,
            max_retries=DEFAULT_MAX_RETRIES,
        )

    def send_message(self, message):
        return send_message(
            message,
            get_timestamp(),
            process_settings=self.process_settings,
            room={"id": self.room_id},
        )
