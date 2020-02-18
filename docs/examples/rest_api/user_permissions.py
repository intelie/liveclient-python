# -*- coding: utf-8 -*-
import sys
import argparse
import eliot

from live_client.utils.logging import log_to_stdout
from live_client.resources.access_control.user import fetch_user_info


def parse_arguments(argv):
    parser = argparse.ArgumentParser(
        description="Validates the requirements for available features"
    )
    parser.add_argument("--live_url", dest="live_url", required=True, help="The url Intelie Live")
    parser.add_argument("--username", dest="username", required=True, help="Live username")
    parser.add_argument("--password", dest="password", required=True, help="Live password")

    return parser.parse_args(argv[1:])


def build_settings(args):
    return {"live": {"url": args.live_url, "username": args.username, "password": args.password}}


if __name__ == "__main__":
    """
    Validates the requirements for available features
    """
    args = parse_arguments(sys.argv)
    settings = build_settings(args)

    userinfo = fetch_user_info(settings, include_teams=True)
    if not userinfo:
        # Error, check the logs
        print("Error. Please check the following log:")
        eliot.add_destinations(log_to_stdout)

    else:
        print("User {name} (id: {id}, email: {email})".format(**userinfo))
        teams = userinfo.get("teams", [])
        if teams:
            for team in teams:
                print("- Team {name}".format(**team))
                roles = team.get("roles", [])
                if roles:
                    for role in roles:
                        print("  - Role {name}".format(**role))
                        permissions = role.get("permissions", [])
                        if permissions:
                            for permission in permissions:
                                print(f"    - Permission {permission}")
