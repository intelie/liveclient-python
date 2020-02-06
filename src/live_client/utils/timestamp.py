# -*- coding: utf-8 -*-
import time

__all__ = ["get_timestamp"]


def get_timestamp():
    return int(time.time() * 1000)
