# -*- coding: utf-8 -*-
from live_client.utils import logging, http

__all__ = ["fetch_resource", "is_live_available"]

HEALTH_OK = "WORKING"


def fetch_resource(path, settings, handle_errors=True):
    live_settings = settings["live"]
    url = live_settings["url"]
    items_url = f"{url}{path}"
    items_list = []

    try:
        items_list = http.request_with_timeout(items_url, settings, handle_errors=handle_errors)
    except Exception:
        if handle_errors:
            logging.exception(f"Error fetching {items_url}")
        else:
            raise

    return items_list


def is_live_available(settings):
    healthcheck_result = fetch_resource("/healthcheck", settings)
    return healthcheck_result == HEALTH_OK
