# -*- coding: utf-8 -*-
import re

from live_client import REQUIREMENTS
from live_client.utils import logging

from .base import fetch_resource

__all__ = ["list_plugins", "list_features"]


REQUIREMENT_RE = re.compile(r"(?P<name>[\w-]+)(?P<comparison>(==|<=|>=|<|>))(?P<version>.*)")
SEMVER_RE = re.compile(r"(?P<major>[\d]+).(?P<minor>[\d]+).(?P<patch>[\d]+)")


def list_plugins(settings, include_disabled=False):
    plugins_info = fetch_resource("/rest/plugin", settings)

    if plugins_info is None:
        plugins_info = {}

    def is_enabled(plugin_data):
        return plugin_data.get("status", {}).get("status") == "VALID"

    plugins_list = [
        item for item in plugins_info.get("data", []) if include_disabled or is_enabled(item)
    ]

    return plugins_list


def list_features(settings):
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

    available_plugins = dict(
        (item.get("name"), item.get("version")) for item in list_plugins(settings)
    )

    features_status = {}
    if available_plugins:
        for module, requirements in REQUIREMENTS.items():
            plugins = requirements.get("plugins", [])
            is_available = True
            messages = []
            for plugin in plugins:
                parsed_requirement = REQUIREMENT_RE.search(plugin).groupdict()
                name = parsed_requirement.get("name")
                comparison = parsed_requirement.get("comparison")
                version = parsed_requirement.get("version")

                if name not in available_plugins:
                    is_available = False
                    message = f"{plugin} expected, but not installed"
                    logging.warn(message)

                else:
                    is_available = is_available and matches_requirement(name, comparison, version)
                    available_version = available_plugins.get(name)
                    message = f"{plugin} expected, {name}=={available_version} found"
                    logging.warn(message)

                messages.append(message)

            features_status.update({module: {"messages": messages, "is_available": is_available}})

    return features_status
