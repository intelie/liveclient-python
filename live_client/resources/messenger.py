# -*- coding: utf-8 -*-
from live_client.utils import logging, http

__all__ = ["list_rooms"]


def list_rooms(process_settings):
    live_settings = process_settings["live"]
    url = live_settings["url"]
    rooms_url = f"{url}/services/plugin-messenger/rooms"
    rooms_list = []

    try:
        rooms_list = http.request_with_timeout(rooms_url, process_settings)
    except Exception:
        logging.exception(f"Error fetching the list of rooms")

    return rooms_list
