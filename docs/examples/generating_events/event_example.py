# -*- coding: utf-8 -*-
import sys
import argparse

from live_client.events import raw


def parse_arguments(argv):
    parser = argparse.ArgumentParser(
        description="Send events to Intelie Live",
        epilog="Reads from standard input and sends an event to live for every line read",
    )
    parser.add_argument("--live_url", dest="live_url", required=True, help="The url Intelie Live")
    parser.add_argument("--username", dest="username", required=True, help="Live username")
    parser.add_argument("--password", dest="password", required=True, help="Live password")
    parser.add_argument(
        "--rest_input", dest="rest_input", required=True, help="Path of the rest input integration"
    )
    parser.add_argument(
        "--event_type",
        dest="event_type",
        default="example_events",
        help="event_type used for the events",
    )

    return parser.parse_args(argv[1:])


def build_settings(args):
    return {
        "live": {
            "url": args.live_url,
            "username": args.username,
            "password": args.password,
            "rest_input": args.rest_input,
        }
    }


if __name__ == "__main__":
    """
    Send events to Intelie Live
    Reads from standard input and sends an event to live for every line read
    """
    args = parse_arguments(sys.argv)
    event_type = args.event_type
    settings = build_settings(args)

    for line in sys.stdin:
        if not line.strip():
            continue

        event = {"__skipstorage": True, "content": line}
        raw.create(event_type, event, settings)
