# -*- coding: utf-8 -*-
import sys
import argparse
from pprint import pprint

from live_client.assets import list_assets, fetch_asset_settings


def parse_arguments(argv):
    parser = argparse.ArgumentParser(description="Displays the details of the registered assets")
    parser.add_argument("--live_url", dest="live_url", required=True, help="The url Intelie Live")
    parser.add_argument("--username", dest="username", required=True, help="Live username")
    parser.add_argument("--password", dest="password", required=True, help="Live password")

    return parser.parse_args(argv[1:])


def build_settings(args):
    return {"live": {"url": args.live_url, "username": args.username, "password": args.password}}


if __name__ == "__main__":
    """
    Displays the details of the registered assets
    """
    args = parse_arguments(sys.argv)
    settings = build_settings(args)

    asset_list = list_assets(settings)
    for item in asset_list:
        aid = item["id"]
        atype = item["asset_type"]
        asset_data = fetch_asset_settings(settings, aid, atype)
        print(f"\nInformation for {atype}/{aid}")
        pprint(asset_data, depth=1)
