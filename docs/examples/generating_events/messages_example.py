# -*- coding: utf-8 -*-
import sys
import argparse

from live_client.events import messenger


def build_parser():
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

    return parser


if __name__ == "__main__":
    """
    Connects to a live instance and watches every query which is started
    For each query, sends a message to one of the messenger's rooms
    """
    parser = build_parser()
    args = parser.parse_args()

    settings = {
        "output": {
            "author": {"id": args.user_id, "name": args.username},
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

    for line in sys.stdin:
        if not line.strip():
            continue

        messenger.send_message(line, process_settings=settings)
