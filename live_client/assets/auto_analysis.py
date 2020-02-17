# -*- coding: utf-8 -*-
import urllib
import uuid

from live_client.utils import http
from live_client.utils.timestamp import get_timestamp
from live_client.events import annotation

__all__ = ["run_analysis", "analyse_and_annotate"]


def run_analysis(settings, **kwargs):
    live_settings = settings["live"]
    url = live_settings["url"]

    qs_data = {
        "assetId": kwargs.get("assetId"),
        "channel": kwargs.get("channel"),
        "qualifier": kwargs.get("channel"),
        "begin": kwargs.get("begin"),
        "end": kwargs.get("end"),
        "computeFields": kwargs.get(
            "computeFields", ["min", "max", "avg", "stdev", "linreg", "derivatives"]
        ),
    }

    params = urllib.parse.urlencode(qs_data, doseq=True)
    analysis_url = f"{url}/services/plugin-liverig-vis/auto-analysis/analyse?{params}"

    return http.request_with_timeout(analysis_url, settings)


def analyse_and_annotate(settings, **kwargs):
    analysis = run_analysis(settings, **kwargs)
    analysis.update(__src="auto-analysis", uid=str(uuid.uuid4()), createdAt=get_timestamp())
    return annotation.create(analysis, settings=settings)
