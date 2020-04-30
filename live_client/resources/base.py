# -*- coding: utf-8 -*-
from live_client.utils import logging, http

__all__ = ["fetch_resource", "is_live_available"]

HEALTH_OK = "WORKING"


def fetch_resource(path, settings, handle_errors=True):
    live_settings = settings["live"]
    url = live_settings["url"]
    resource_url = f"{url}{path}"
    resource = None

    try:
        resource = http.request_with_timeout(resource_url, settings, handle_errors=handle_errors)
    except Exception:
        if handle_errors: # !!! We only get here if handle_errors == False so we don't need to test <<<<<
            logging.exception(f"Error fetching {resource_url}")
        else:
            raise

    return resource


def is_live_available(settings):
    healthcheck_result = fetch_resource("/healthcheck", settings)
    return healthcheck_result == HEALTH_OK
