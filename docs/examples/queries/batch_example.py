# -*- coding: utf-8 -*-
from live_client.query import on_event


read_timeout = 10
settings = {
    "live": {
        "url": "http://localhost:8080",
        "username": "admin",  # Username as a string
        "password": "admin",  # Password, as a string
    }
}


if __name__ == "__main__":
    """
    Returns the number of running queries, considering only
    queries started over the last hour
    """

    example_query = "__queries => id, action, expression"
    span = "last hour"

    @on_event(example_query, settings, span=span, realtime=False, timeout=read_timeout)
    def handle_events(event, accumulator):
        event_data = event.get("data", {})
        content = event_data.get("content", {})
        for item in content:
            qid = item["id"]
            action = item["action"]
            expression = item["expression"]

            if action == "start":
                accumulator[qid] = expression
            elif action == "stop" and qid in accumulator:
                del accumulator[qid]

        return

    accumulator = {}
    handle_events(accumulator=accumulator)
    print("{} active queries".format(len(accumulator)))
