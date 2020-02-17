# -*- coding: utf-8

REQUIRED_PLUGINS = {
    "live_client.assets": ["plugin-liverig>=2.17.0"],
    "live_client.assets.auto_analysis": [
        "plugin-liverig-vis>=2.17.0",
        "plugin-annotations>=2.24.5",
        "plugin-restinput>=2.25.0",
    ],
    "live_client.connection.rest_input": ["plugin-restinput>=2.25.0"],
    "live_client.connection.tcp_input": ["plugin-tcpinput>=2.24.0"],
    "live_client.events.annotation": ["plugin-annotations>=2.24.5", "plugin-restinput>=2.25.0"],
    "live_client.events.messenger": ["plugin-messenger>=2.24.0"],
    "live_client.resources.dashboards": ["live-ui>=2.24.0"],
    "live_client.resources.messenger": ["plugin-messenger>=2.24.0"],
}
