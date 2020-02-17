# -*- coding: utf-8 -*-

from live_client.utils import http

__all__ = ["fetch_curves"]


def fetch_curves(settings):
    live_settings = settings["live"]
    host = live_settings["host"]

    url = "{}/services/plugin-liverig/curves/".format(host)

    data = http.request_with_timeout(url, settings)
    return data
