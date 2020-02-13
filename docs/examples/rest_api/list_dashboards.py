# -*- coding: utf-8 -*-
import sys
import argparse
import eliot

from live_client.utils.logging import log_to_stdout
from live_client.resources.dashboards import list_dashboards


def parse_arguments(argv):
    parser = argparse.ArgumentParser(
        description="Displays the list of dashboards on an Intelie Live instance"
    )
    parser.add_argument("--live_url", dest="live_url", required=True, help="The url Intelie Live")
    parser.add_argument("--username", dest="username", required=True, help="Live username")
    parser.add_argument("--password", dest="password", required=True, help="Live password")

    return parser.parse_args(argv[1:])


def build_settings(args):
    return {"live": {"url": args.live_url, "username": args.username, "password": args.password}}


if __name__ == "__main__":
    """
    Displays the list of dashboards on an Intelie Live instance
    """
    args = parse_arguments(sys.argv)
    settings = build_settings(args)

    dashboards_info = list_dashboards(settings)
    if dashboards_info is None:
        # Error, check the logs
        print("Error. Please check the following log:")
        eliot.add_destinations(log_to_stdout)

    else:
        dash_count = dashboards_info['total']
        print(f"There are {dash_count} dashboards on {args.live_url}")

        template = "- Dashboard {id:-3d}, url: {url:16s}, title: {title}"
        dash_list = dashboards_info['data']
        for item in dash_list:
            print(template.format(**item))
