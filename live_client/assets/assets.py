# -*- coding: utf-8 -*-
from multiprocessing import Queue

from live_client import query
from live_client.utils import logging, http

__all__ = ["list_assets", "fetch_asset_settings", "watch_asset_settings"]


ALL_ASSET_TYPES = ["rig", "crew", "pump"]


def list_assets(settings, asset_type=None):
    live_settings = settings["live"]
    url = live_settings["url"]
    data = []

    if asset_type in ALL_ASSET_TYPES:
        chosen_asset_types = [asset_type]

    elif asset_type is None:
        chosen_asset_types = ALL_ASSET_TYPES

    else:
        chosen_asset_types = []

    for atype in chosen_asset_types:
        asset_url = f"{url}/services/plugin-liverig/assets/{atype}"
        try:
            response_data = http.request_with_timeout(asset_url, settings)
            if response_data is not None:
                for asset in response_data:
                    asset["asset_type"] = atype
                    data.append(asset)
        except Exception:
            logging.exception(f"Error fetching asset list for {atype}")

    return data


def fetch_asset_settings(settings, asset_id, asset_type="rig"):
    live_settings = settings["live"]
    url = live_settings["url"]
    asset_url = f"{url}/services/plugin-liverig/assets/{asset_type}/{asset_id}/normalizer"
    return http.request_with_timeout(asset_url, settings)


def watch_asset_settings(settings, asset_id, asset_type="rig"):
    initial_config = fetch_asset_settings(settings, asset_id, asset_type=asset_type)

    asset_query_template = "__asset event:(normalizer|delete) type:{} id:{}"
    asset_query = asset_query_template.format(asset_type, asset_id)
    results_process, results_queue = query.run(settings, asset_query, realtime=True)

    results_queue.put({"config": initial_config})
    return _settings_update_handler(results_queue)


def _settings_update_handler(events_queue):
    settings_queue = Queue()

    while True:
        event = events_queue.get()
        settings_queue.put(event.get("config", {}))

    return settings_queue
