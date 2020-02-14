# -*- coding: utf-8 -*-
from .base import fetch_resource

__all__ = ["list_dashboards"]


def list_dashboards(settings):
    return fetch_resource("/rest/dashboard", settings)
