# -*- coding: utf-8 -*-
from .base import fetch_resource

__all__ = ["list_plugins"]


def list_plugins(settings, include_disabled=False):
    plugins_info = fetch_resource("/rest/plugin", settings)

    if plugins_info is None:
        plugins_info = {}

    def is_enabled(plugin_data):
        return plugin_data.get("status", {}).get("status") == "VALID"

    plugins_list = [
        item for item in plugins_info.get("data", []) if include_disabled or is_enabled(item)
    ]

    return plugins_list
