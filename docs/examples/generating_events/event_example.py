# -*- coding: utf-8 -*-
import sys
from live_client.events import raw


settings = {
    "live": {
        "url": "http://localhost:8080",
        "username": "admin",  # Username as a string
        "password": "admin",  # Password, as a string
        "rest_input": "/services/plugin-restinput/shell/",
    }
}


if __name__ == "__main__":
    """
    Reads from standard input and sends an event to live for every line read.
    Note: The generated event will not be stored on live.
    """

    event_type = "example_events"

    for line in sys.stdin:
        if not line.strip():
            continue

        event = {"__skipstorage": True, "content": line}
        raw.create(event_type, event, settings)
