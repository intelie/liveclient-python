# -*- coding: utf-8 -*-
from live_client.resources.base import fetch_resource

__all__ = ["fetch_role_info", "fetch_roles_info"]


def fetch_role_info(role_id, settings):
    return fetch_roles_info([role_id], settings)


def fetch_roles_info(role_ids, settings):
    # Fetch all roles. Larger payload instead of more requests
    response = fetch_resource("/rest/role", settings)
    all_roles = response.get("data", [])
    return [item for item in all_roles if item["id"] in role_ids]
