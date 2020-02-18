# -*- coding: utf-8 -*-
from live_client.resources.base import fetch_resource
from .role import fetch_roles_info

__all__ = ["fetch_team_info", "fetch_teams_info"]


def fetch_team_info(team_id, settings):
    return fetch_teams_info([team_id], settings)


def fetch_teams_info(team_ids, settings):
    # Fetch all teams. Larger payload instead of more requests
    response = fetch_resource("/rest/team", settings)
    all_teams = response.get("data", [])
    selected_teams = [item for item in all_teams if item["id"] in team_ids]

    # Fetch the data for roles related to the teams
    role_ids = []
    for item in selected_teams:
        role_ids.extend(role["id"] for role in item.get("roles", []))

    selected_roles = fetch_roles_info(set(role_ids), settings)

    # Add the roles for each team
    roles_by_id = dict((item["id"], item) for item in selected_roles)

    for team in selected_teams:
        team.update(roles=[roles_by_id.get(item["id"]) for item in team.get("roles", [])])

    return selected_teams
