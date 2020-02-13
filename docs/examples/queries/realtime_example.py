# -*- coding: utf-8 -*-
from live_client.query import on_event


read_timeout = 120
settings = {
    "live": {
        "url": "http://localhost:8080",
        "username": "admin",  # Username as a string
        "password": "admin",  # Password, as a string
    }
}


if __name__ == "__main__":
    """
    Connects to a live instance and prints every query which is started
    """

    example_query = "__queries action:start => expression, description"

    @on_event(example_query, settings, timeout=read_timeout)
    def handle_events(event, settings=None):
        event_data = event.get("data", {})
        content = event_data.get("content", {})
        template = "New query: '{}'"
        for item in content:
            message = template.format(item["expression"])
            print(message)

        return

    handle_events(settings=settings)
