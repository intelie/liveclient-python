# -*- coding: utf-8 -*-
import argparse

from live_client.query import on_event


def build_parser():
    parser = argparse.ArgumentParser(
        description="Writes each query started on Intelie Live to the standard output"
    )
    parser.add_argument("--live_url", dest="live_url", required=True, help="The url Intelie Live")
    parser.add_argument("--username", dest="username", required=True, help="Live username")
    parser.add_argument("--password", dest="password", required=True, help="Live password")

    return parser


if __name__ == "__main__":
    """
    Connects to a live instance and prints every query which is started
    """
    parser = build_parser()
    args = parser.parse_args()

    settings = {
        "live": {"url": args.live_url, "username": args.username, "password": args.password}
    }

    example_query = "__queries action:start => expression, description"

    @on_event(example_query, settings, timeout=120)
    def handle_events(event, settings=None):
        event_data = event.get("data", {})
        content = event_data.get("content", {})
        template = "New query: '{}'"
        for item in content:
            message = template.format(item["expression"])
            print(message)

        return

    handle_events(settings=settings)
