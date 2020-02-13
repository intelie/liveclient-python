# -*- coding: utf-8 -*-
from live_client.utils import logging, http

__all__ = ["fetch_resource"]


def fetch_resource(path, process_settings):
    live_settings = process_settings["live"]
    url = live_settings["url"]
    items_url = f"{url}{path}"
    items_list = []

    try:
        items_list = http.request_with_timeout(items_url, process_settings)
    except Exception:
        logging.exception(f"Error fetching {items_url}")

    return items_list
