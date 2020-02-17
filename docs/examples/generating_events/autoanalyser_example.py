# -*- coding: utf-8 -*-
import sys
import argparse
import eliot
import itertools

from live_client.utils.logging import log_to_stdout
from live_client.resources.messenger import list_rooms
from live_client.assets import list_assets, fetch_asset_settings
from live_client.query import on_event
from live_client.utils.timestamp import get_timestamp
from live_client.assets import analyse_and_annotate


def parse_arguments(argv):
    parser = argparse.ArgumentParser(
        description="Executes the auto analyser and publishes the results to the global room"
    )
    parser.add_argument("--live_url", dest="live_url", required=True, help="The url Intelie Live")
    parser.add_argument("--username", dest="username", required=True, help="Live username")
    parser.add_argument("--password", dest="password", required=True, help="Live password")
    parser.add_argument(
        "--rest_input", dest="rest_input", required=True, help="Path of the rest input integration"
    )
    parser.add_argument("--user_id", dest="user_id", required=True, help="Live user id")

    return parser.parse_args(argv[1:])


def build_settings(args):
    return {
        "output": {"author": {"id": args.user_id, "name": "🤖 Analyser bot "}},
        "live": {
            "url": args.live_url,
            "rest_input": args.rest_input,
            "username": args.username,
            "password": args.password,
            "user_id": args.user_id,
        },
    }


def results_or_logs(results):
    if results is None:
        # Error, check the logs
        print("Error. Please check the following log:")
        eliot.add_destinations(log_to_stdout)
        raise SystemExit(1)

    return results


def get_global_room(settings):
    expected_type = "Global"
    print(f"Looking for the {expected_type} room")

    rooms_list = results_or_logs(list_rooms(settings))
    global_rooms = [room for room in rooms_list if room.get("type") == expected_type]

    if global_rooms:
        result = global_rooms[0]
    else:
        result = None

    return result


def get_assets(settings):
    print("Fetching the list of event types for the assets")
    asset_list = results_or_logs(list_assets(settings))
    for item in asset_list:
        asset_id = item["id"]
        asset_type = item["asset_type"]
        item.update(**results_or_logs(fetch_asset_settings(settings, asset_id, asset_type)))

    return asset_list


def get_active_channels(assets, settings):
    print(f"Getting active channels for {len(assets)} assets")
    event_types = [item.get("event_type") for item in assets]

    active_channels_query = """
        ({})
        => __type, mnemonic, mnemonic:count() as count by asset_id, mnemonic at the end
        => @sort __type, count desc
    """.format(
        " | ".join(event_types)
    )

    @on_event(active_channels_query, settings, realtime=False, span="last minute", preload=True)
    def run_query(event):
        event_data = event.get("data", {})
        return event_data.get("content", {})

    return run_query()


def analyse_channels(assets, active_channels, settings):
    ONE_MINUTE = 60000

    if active_channels:
        assets_by_etype = dict((item.get("event_type"), item) for item in assets)

        channels_by_asset = itertools.groupby(active_channels, key=lambda x: x.get("__type"))
        for event_type, channels in channels_by_asset:
            asset = assets_by_etype.get(event_type)
            channel = next(channels)
            channel_name = channel.get("mnemonic")
            end = get_timestamp()
            begin = end - ONE_MINUTE

            print(f"Analysing channel {channel_name} for {event_type}")
            analyse_and_annotate(
                settings,
                assetId="{0[asset_type]}/{0[id]}".format(asset),
                channel=channel_name,
                begin=begin,
                end=end,
            )
    else:
        print("No channels to analyse")
        raise SystemExit(0)


if __name__ == "__main__":
    """
    Executes the auto analyser and publishes the results to the global room.
    This is a multi-step process, and demonstrates many of the existing features

    Step 1: Find the global room
    Step 2: Get the list of event types for the assets
    Step 3: Find out the list of active channels for the assets on the last minute
    Step 4: Analyse the most active channel for each of the assets publish to the global room
    """
    args = parse_arguments(sys.argv)
    settings = build_settings(args)

    # Step 1: Find the id of the global room and add it to the settings
    global_room = get_global_room(settings)
    settings["output"]["room"] = {"id": global_room["id"]}

    # Step 2: Get the list of event types for the assets
    assets = get_assets(settings)

    # Step 3: Find out the list of active channels for the assets on the last minute
    active_channels = get_active_channels(assets, settings)

    # Step 4: Analyse the most active channel for each of the assets publish to the global room
    analysis_list = analyse_channels(assets, active_channels, settings)
