# -*- coding: utf-8 -*-
import sys
import argparse

from live_client.events import messenger


def parse_arguments(argv):
    parser = argparse.ArgumentParser(
        description="Send messages to one of the messenger rooms on Intelie Live",
        epilog="Reads from standard input and sends a message for every line read",
    )
    parser.add_argument("--live_url", dest="live_url", required=True, help="The url Intelie Live")
    parser.add_argument("--username", dest="username", required=True, help="Live username")
    parser.add_argument("--password", dest="password", required=True, help="Live password")
    parser.add_argument(
        "--rest_input", dest="rest_input", required=True, help="Path of the rest input integration"
    )
    parser.add_argument("--user_id", dest="user_id", required=True, help="Live user id")
    parser.add_argument("--room_id", dest="room_id", required=True, help="Target room id")

    return parser.parse_args(argv[1:])


def build_settings(args):
    return {
        "output": {
            "author": {"id": args.user_id, "name": "🤖  Messages bot "},
            "room": {"id": args.room_id},
        },
        "live": {
            "url": args.live_url,
            "rest_input": args.rest_input,
            "username": args.username,
            "password": args.password,
            "user_id": args.user_id,
        },
    }


if __name__ == "__main__":
    """
    Send messages to one of the messenger rooms on Intelie Live
    Reads from standard input and sends a message for every line read
    """
    args = parse_arguments(sys.argv)
    settings = build_settings(args)

    messenger.join_messenger(settings)

    print("\vAll messages written here will be sent to Live. Press CTRL+D to exit.\n")
    for line in sys.stdin:
        if not line.strip():
            continue

        messenger.send_message(line, settings=settings)
