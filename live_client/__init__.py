# -*- coding: utf-8
from .resources.access_control import permissions

REQUIREMENTS = {
    "live_client.query": {"permissions": [permissions.CONSOLE]},
    "live_client.assets": {
        "plugins": ["plugin-liverig>=2.17.0"],
        "permissions": [permissions.ASSETS],
    },
    "live_client.assets.auto_analysis": {
        "plugins": [
            "plugin-liverig-vis>=2.17.0",
            "plugin-annotations>=2.24.5",
            "plugin-restinput>=2.25.0",
        ],
        "permissions": [permissions.ASSETS],
    },
    "live_client.connection.rest_input": {"plugins": ["plugin-restinput>=2.25.0"]},
    "live_client.connection.tcp_input": {"plugins": ["plugin-tcpinput>=2.24.0"]},
    "live_client.events.annotation": {
        "plugins": ["plugin-annotations>=2.24.5", "plugin-restinput>=2.25.0"],
        "permissions": [permissions.EDIT_ANNOTATIONS],
    },
    "live_client.events.messenger": {"plugins": ["plugin-messenger>=2.24.0"]},
    "live_client.resources.dashboards": {
        "plugins": ["live-ui>=2.24.0"],
        "permissions": [permissions.DASHBOARDS],
    },
    "live_client.resources.messenger": {
        "plugins": ["plugin-messenger>=2.24.0"],
        "permissions": [permissions.USE_MESSENGER],
    },
}
