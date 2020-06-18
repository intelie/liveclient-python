# -*- coding: utf-8 -*-
import sys
import argparse

from live_client.query import on_event


def parse_arguments(argv):
    parser = argparse.ArgumentParser(
        description="Writes each query started on Intelie Live to the standard output"
    )
    parser.add_argument("--live_url", dest="live_url", required=True, help="The url Intelie Live")
    parser.add_argument("--username", dest="username", required=True, help="Live username")
    parser.add_argument("--password", dest="password", required=True, help="Live password")

    return parser.parse_args(argv[1:])


def build_settings(args):
    return {"live": {"url": args.live_url, "username": args.username, "password": args.password}}


if __name__ == "__main__":
    """
    Connects to a live instance and fetches a list of queries from mongodb every minute
    """
    args = parse_arguments(sys.argv)
    settings = build_settings(args)

    example_query = """
      // @cron * * * * *
      // @noeval
      {
          find: "events.__queries",
          filter: {"action": "start" },
          projection: {expression: 1, description: 1}
      }
    """

    @on_event(example_query, settings, timeout=120, provider="mongodb")
    def handle_events(event):
        event_data = event.get("data", {})
        content = event_data.get("content", {})
        for item in content:
            cursor = item["cursor"]
            results = cursor.get("firstBatch", [])
            expressions = set(item["expression"] for item in results)

            print(f"{len(results)} queries, {len(expressions)} distinct queries")
            for expression in expressions:
                print(f'{"-" * 80}\n{expression}')

        return

    print("\vListing queries every minute. Press CTRL+C to exit.\n")
    handle_events()
