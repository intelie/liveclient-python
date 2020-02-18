# -*- coding: utf-8 -*-
from live_client.resources.base import fetch_resource
from .team import fetch_teams_info

__all__ = ["fetch_user_info"]


def fetch_user_info(settings, include_teams=False):
    user = fetch_resource("/rest/me", settings)

    if user is not None:
        user_teams = user.get("teams", [])

        if include_teams and user_teams:
            team_ids = [item["id"] for item in user_teams]
            user_teams = fetch_teams_info(team_ids, settings)
            user.update(teams=user_teams)

    return user
