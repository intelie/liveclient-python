# -*- coding: utf-8 -*-
import sys
import argparse

from live_client.utils.timestamp import get_timestamp
from live_client.events import annotation


def parse_arguments(argv):
    parser = argparse.ArgumentParser(
        description="Creates annotations in one of the rooms and/or dashboards on Intelie Live",
        epilog="Reads from standard input and creates an annotation for every line read",
    )
    parser.add_argument("--live_url", dest="live_url", required=True, help="The url Intelie Live")
    parser.add_argument("--username", dest="username", required=True, help="Live username")
    parser.add_argument("--password", dest="password", required=True, help="Live password")
    parser.add_argument(
        "--rest_input", dest="rest_input", required=True, help="Path of the rest input integration"
    )
    parser.add_argument("--user_id", dest="user_id", required=True, help="Live user id")
    parser.add_argument("--room_id", dest="room_id", help="Target room id")
    parser.add_argument("--dashboard_id", dest="dashboard_id", help="Target dashboard id")
    parser.add_argument("--author_name", dest="author_name", help="Annotation author name")
    parser.add_argument("--src", dest="src", help="Source for the annotation")
    parser.add_argument(
        "--ts_delta", dest="ts_delta", default=0, help="Delta to apply to the timestamp"
    )

    args = parser.parse_args(argv[1:])
    if not any([args.room_id, args.dashboard_id]):
        parser.error("Either --room_id or --dashboard_id are required")

    return args


def build_settings(args):
    author_name = args.author_name or "🤖  Annotations bot "

    settings = {
        "output": {
            "author": {"id": args.user_id, "name": author_name},
            "room": {"id": args.room_id},
            "dashboard": {"id": args.dashboard_id, "name": "the dashboard"},
        },
        "live": {
            "url": args.live_url,
            "rest_input": args.rest_input,
            "username": args.username,
            "password": args.password,
            "user_id": args.user_id,
        },
    }

    if not args.room_id:
        del settings["output"]["room"]
    if not args.dashboard_id:
        del settings["output"]["dashboard"]

    return settings


if __name__ == "__main__":
    """
    Creates annotations in one of the rooms and/or dashboards on Intelie Live
    Reads from standard input and creates an annotation for every line read
    """
    args = parse_arguments(sys.argv)
    settings = build_settings(args)
    __src = getattr(args, "src") or "live-client"
    ts_delta = int(args.ts_delta)

    print("\vAll messages written here will be sent to Live. Press CTRL+D to exit.\n")
    for line in sys.stdin:
        if not line.strip():
            continue

        ts = get_timestamp() + ts_delta
        annotation.create(
            {"message": line, "__src": __src, "timestamp": ts, "createdAt": ts}, settings=settings
        )
