# Live Client

A toolset to interact with the Intelie LIVE Platform


## Usage example

```python
# -*- coding: utf-8 -*-
from live_client.query import on_event
from live_client.events import messenger


read_timeout = 120
settings = {
    "output": {
        "author": {"id": 2, "name": "🤖 Query watcher"},
        "room": {"id": "f1v7nljg8on2v2h5tm6v9bmdug"},
    },
    "live": {
        "ip": "127.0.0.1",
        "port": 17042,
        "url": "http://localhost:8080",
        "rest_input": "/services/plugin-restinput/shell/",
        "username": "<USERNAME>",  # Username as a string
        "password": "<PASSWORD>",  # Password, as a string
        "user_id": 1,  # The user's id on live, as an integer
        "user_name": "🤖 Automated Nofification",  # The user's name
    },
}


if __name__ == "__main__":
    """
    Connects to a live instance and watches every query which is started
    For each query, sends a message to one of the messenger's rooms
    """

    example_query = "__queries action:start => expression, description"
    span = f"last 60 seconds"

    @on_event(example_query, settings, span=span, timeout=read_timeout)
    def handle_events(event, settings=None):
        event_data = event.get("data", {})
        content = event_data.get("content", {})
        template = "New query: '{}'"
        for item in content:
            message = template.format(item["expression"])
            print(message)
            messenger.send_message(
                message, timestamp=item["timestamp"], process_settings=settings
            )

        return

    handle_events(settings=settings)
```
