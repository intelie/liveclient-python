# -*- coding: utf-8 -*-
import sys

__all__ = ["get_start_method"]


METHODS_BY_PLATFORM = {"win32": "spawn", "darwin": "spawn", "linux": "fork"}


def get_start_method(default="fork"):
    return METHODS_BY_PLATFORM.get(sys.platform, default)
