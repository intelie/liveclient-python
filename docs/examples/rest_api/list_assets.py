# -*- coding: utf-8 -*-
import sys
import argparse
import eliot

from live_client.utils.logging import log_to_stdout
from live_client.assets import list_assets


def parse_arguments(argv):
    parser = argparse.ArgumentParser(
        description="Displays the list of assets on an Intelie Live instance"
    )
    parser.add_argument("--live_url", dest="live_url", required=True, help="The url Intelie Live")
    parser.add_argument("--username", dest="username", required=True, help="Live username")
    parser.add_argument("--password", dest="password", required=True, help="Live password")

    return parser.parse_args(argv[1:])


def build_settings(args):
    return {"live": {"url": args.live_url, "username": args.username, "password": args.password}}


if __name__ == "__main__":
    """
    Displays the list of assets on an Intelie Live instance
    """
    args = parse_arguments(sys.argv)
    settings = build_settings(args)

    asset_list = list_assets(settings)
    if asset_list is None:
        # Error, check the logs
        print("Error. Please check the following log:")
        eliot.add_destinations(log_to_stdout)

    else:
        print(f"List of assets on {args.live_url}")
        template = "- Type: {asset_type}, id: {asset_type}/{id}, name: {name}"
        for item in asset_list:
            print(template.format(**item))
