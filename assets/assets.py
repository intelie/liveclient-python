# -*- coding: utf-8 -*-
from multiprocessing import Queue

from .utils import make_request
from live_client import query

__all__ = [
    'list_assets',
    'fetch_asset_settings',
    'watch_asset_settings',
]


def list_assets(process_name, process_settings, output_info, asset_type='rig'):
    live_settings = process_settings['live']
    host = live_settings['host']

    url = '{}/services/plugin-liverig/assets/{}'.format(host, asset_type)

    data = make_request(process_name, process_settings, output_info, url)
    return data


def fetch_asset_settings(process_name, process_settings, output_info, asset_id, asset_type='rig'):
    live_settings = process_settings['live']
    host = live_settings['host']

    url = '{}/services/plugin-liverig/assets/{}/{}/normalizer'.format(host, asset_type, asset_id)
    return make_request(process_name, process_settings, output_info, url)


def watch_asset_settings(process_name, process_settings, output_info, asset_id, asset_type='rig'):
    initial_config = fetch_asset_settings(
        process_name,
        process_settings,
        output_info,
        asset_id,
        asset_type=asset_type
    )

    asset_query_template = '__asset event:(normalizer|delete) type:{} id:{}'
    asset_query = asset_query_template.format(asset_type, asset_id)
    results_process, results_queue = query.run(
        process_name,
        process_settings,
        asset_query,
        realtime=True,
    )

    results_queue.put({'config': initial_config})
    return _settings_update_handler(results_queue)


def _settings_update_handler(events_queue):
    settings_queue = Queue()

    while True:
        event = events_queue.get()
        settings_queue.put(event.get('config', {}))

    return settings_queue
