# -*- coding: utf-8 -*-
import sys
import argparse
import eliot

from live_client.utils.logging import log_to_stdout
from live_client.resources.plugins import list_plugins


def parse_arguments(argv):
    parser = argparse.ArgumentParser(
        description="Validates the requirements for available features"
    )
    parser.add_argument("--live_url", dest="live_url", required=True, help="The url Intelie Live")
    parser.add_argument("--username", dest="username", required=True, help="Live username")
    parser.add_argument("--password", dest="password", required=True, help="Live password")

    return parser.parse_args(argv[1:])


def build_settings(args):
    return {"live": {"url": args.live_url, "username": args.username, "password": args.password}}


if __name__ == "__main__":
    """
    Validates the requirements for available features
    """
    args = parse_arguments(sys.argv)
    settings = build_settings(args)

    plugins = list_plugins(settings)
    if not plugins:
        # Error, check the logs
        print("Error. Please check the following log:")
        eliot.add_destinations(log_to_stdout)

    else:
        plugin_count = len(plugins)
        print(f"There are {plugin_count} enabled plugins {args.live_url}")

        template = "- {name} version {version}"
        for item in plugins:
            print(template.format(**item))
