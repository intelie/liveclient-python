# -*- coding: utf-8 -*-
import argparse

from live_client.query import on_event


def build_parser():
    parser = argparse.ArgumentParser(
        description="Returns the number of active queries on Intelie Live"
    )
    parser.add_argument("--live_url", dest="live_url", required=True, help="The url Intelie Live")
    parser.add_argument("--username", dest="username", required=True, help="Live username")
    parser.add_argument("--password", dest="password", required=True, help="Live password")

    return parser


if __name__ == "__main__":
    """
    Returns the number of running queries, considering only
    queries started over the last hour
    """
    parser = build_parser()
    args = parser.parse_args()

    settings = {
        "live": {"url": args.live_url, "username": args.username, "password": args.password}
    }

    example_query = "__queries => id, action, expression"
    span = "last hour"

    @on_event(example_query, settings, span=span, realtime=False, timeout=10)
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
