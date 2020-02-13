# -*- coding: utf-8 -*-
from multiprocessing import Queue
from functools import partial
import urllib

from live_client import query
from live_client.utils import logging

from .utils import make_request

__all__ = ["list_assets", "fetch_asset_settings", "watch_asset_settings", "run_analysis"]


ALL_ASSET_TYPES = ["rig", "crew", "pump"]


request_with_timeout = partial(make_request, timeout=(3.05, 5), max_retries=5)


def list_assets(process_settings, asset_type=None):
    live_settings = process_settings["live"]
    url = live_settings["url"]
    data = []

    if asset_type in ALL_ASSET_TYPES:
        chosen_asset_types = [asset_type]

    elif asset_type is None:
        chosen_asset_types = ALL_ASSET_TYPES

    else:
        chosen_asset_types = []

    for atype in chosen_asset_types:
        url = f"{url}/services/plugin-liverig/assets/{atype}"
        try:
            response_data = request_with_timeout(process_settings, url)
            if response_data is not None:
                for asset in response_data:
                    asset["asset_type"] = atype
                    data.append(asset)
        except Exception:
            logging.exception(f"Error fetching asset list for {atype}")

    return data


def fetch_asset_settings(process_settings, asset_id, asset_type="rig"):
    live_settings = process_settings["live"]
    url = live_settings["url"]

    url = f"{url}/services/plugin-liverig/assets/{asset_type}/{asset_id}/normalizer"
    return request_with_timeout(process_settings, url)


def watch_asset_settings(process_settings, asset_id, asset_type="rig"):
    initial_config = fetch_asset_settings(process_settings, asset_id, asset_type=asset_type)

    asset_query_template = "__asset event:(normalizer|delete) type:{} id:{}"
    asset_query = asset_query_template.format(asset_type, asset_id)
    results_process, results_queue = query.run(process_settings, asset_query, realtime=True)

    results_queue.put({"config": initial_config})
    return _settings_update_handler(results_queue)


def _settings_update_handler(events_queue):
    settings_queue = Queue()

    while True:
        event = events_queue.get()
        settings_queue.put(event.get("config", {}))

    return settings_queue


def run_analysis(process_settings, **kwargs):
    live_settings = process_settings["live"]
    url = live_settings["url"]

    qs_data = {
        "assetId": kwargs.get("assetId"),
        "channel": kwargs.get("channel"),
        "qualifier": kwargs.get("channel"),
        "begin": kwargs.get("begin"),
        "end": kwargs.get("end"),
        "computeFields": kwargs.get("computeFields"),
    }

    params = urllib.parse.urlencode(qs_data, doseq=True)
    analysis_url = f"{url}/services/plugin-liverig-vis/auto-analysis/analyse?{params}"

    return request_with_timeout(process_settings, analysis_url)
