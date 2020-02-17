# -*- coding: utf-8 -*-

__all__ = ["only_enabled_curves"]


def only_enabled_curves(curves):
    idle_curve = [{}]

    return dict(
        (name, value)
        for (name, value) in curves.items()
        if value.get("options", idle_curve) != idle_curve
    )
