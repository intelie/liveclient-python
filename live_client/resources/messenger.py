# -*- coding: utf-8 -*-
from .base import fetch_resource

__all__ = ["list_rooms"]


def list_rooms(process_settings):
    return fetch_resource("/services/plugin-messenger/rooms", process_settings)
