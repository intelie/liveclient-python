# -*- coding: utf-8 -*-
import re

from live_client import REQUIREMENTS
from live_client.resources.plugins import list_plugins
from live_client.resources.access_control.user import fetch_user_info
from . import logging
from .colors import TextColors

__all__ = ["check_status", "prepare_report"]

REQUIREMENT_RE = re.compile(r"(?P<name>[\w-]+)(?P<comparison>(==|<=|>=|<|>))(?P<version>.*)")
SEMVER_RE = re.compile(r"(?P<major>[\d]+).(?P<minor>[\d]+).(?P<patch>[\d]+)")


def check_status(settings):
    """
    Validates the requirements for available features
    """

    def parse_version(version_data):
        match = SEMVER_RE.search(version_data)
        if match is None:
            parsed = (0, 0, 0)
        else:
            parsed = tuple(map(int, match.groups()))

        return parsed

    def compare_versions(x, y, comparison="=="):
        comparators = {
            "==": lambda a, b: a == b,
            "<=": lambda a, b: a <= b,
            ">=": lambda a, b: a >= b,
            "<": lambda a, b: a < b,
            ">": lambda a, b: a > b,
        }
        return comparators.get(comparison)(x, y)

    def matches_requirement(name, comparison, version_spec):
        available_version = parse_version(available_plugins.get(name))
        expected_version = parse_version(version_spec)
        return compare_versions(available_version, expected_version, comparison)

    def merge_user_permissions(userinfo):
        if userinfo:
            permissions = []
            for team in userinfo.get("teams", []):
                for role in team.get("roles", []):
                    permissions.extend(role.get("permissions", []))
        else:
            permissions = []

        return set(permissions)

    def prepare_message(text, sucess=True):
        if sucess:
            color = ""
        else:
            color = TextColors.UNDERLINE
            logging.warn(text)

        return f"{color}{text}{TextColors.ENDC}"

    available_plugins = dict(
        (item.get("name"), item.get("version")) for item in list_plugins(settings)
    )
    user_permissions = merge_user_permissions(fetch_user_info(settings, include_teams=True))

    features_status = {}
    if available_plugins:
        for module, requirements in REQUIREMENTS.items():
            messages = []
            is_available = True

            for plugin in requirements.get("plugins", []):
                parsed_requirement = REQUIREMENT_RE.search(plugin).groupdict()
                name = parsed_requirement.get("name")
                comparison = parsed_requirement.get("comparison")
                version = parsed_requirement.get("version")

                if name not in available_plugins:
                    is_available = False
                    message = prepare_message(f"{plugin} expected, but not installed", sucess=False)

                else:
                    has_expected_version = matches_requirement(name, comparison, version)
                    is_available = is_available and has_expected_version
                    available_version = available_plugins.get(name)
                    message = prepare_message(
                        f"{plugin} expected, {name}=={available_version} found",
                        sucess=has_expected_version,
                    )

                messages.append(prepare_message(message, has_expected_version))

            for permission in requirements.get("permissions", []):
                if permission not in user_permissions:
                    is_available = False
                    message = prepare_message(
                        f"User does not have permission '{permission}'", sucess=False
                    )
                else:
                    message = f"Permission '{permission}' is present"

                messages.append(message)

            features_status.update({module: {"messages": messages, "is_available": is_available}})

    return features_status


def prepare_report(settings, *status_containers):
    result = [f"\v{TextColors.BOLD}Status for {settings['live']['url']}{TextColors.ENDC}"]

    for statuses in status_containers:
        for key, status in statuses.items():
            messages = status.get("messages")
            is_available = status.get("is_available")
            if is_available:
                availability = "AVAILABLE"
                color = TextColors.OKGREEN
            else:
                availability = "UNAVAILABLE"
                color = TextColors.FAIL

            result.append(f"\v{color}{key} is {availability}{TextColors.ENDC}:")
            for item in messages:
                result.append(f"- {item}")

    result.append("\v")

    return result
