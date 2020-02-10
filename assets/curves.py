# -*- coding: utf-8 -*-

from .utils import make_request

__all__ = ["fetch_curves"]


def fetch_curves(process_settings):
    live_settings = process_settings["live"]
    host = live_settings["host"]

    url = "{}/services/plugin-liverig/curves/".format(host)

    data = make_request(process_settings, url)
    return data
