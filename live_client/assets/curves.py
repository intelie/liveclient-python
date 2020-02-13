# -*- coding: utf-8 -*-

from live_client.utils import http

__all__ = ["fetch_curves"]


def fetch_curves(process_settings):
    live_settings = process_settings["live"]
    host = live_settings["host"]

    url = "{}/services/plugin-liverig/curves/".format(host)

    data = http.request_with_timeout(url, process_settings)
    return data
