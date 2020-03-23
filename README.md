# Live Client

A toolset to interact with the Intelie LIVE Platform


## Usage examples

```
import sys
import argparse

from live_client.query import on_event
from live_client.events import messenger


def parse_arguments(argv):
    parser = argparse.ArgumentParser(
        description="Connects to a live instance and watches every query which is started",
        epilog="For each query, sends a message to one of the messenger's rooms"
    )
    parser.add_argument("--live_url", dest="live_url", required=True, help="The url Intelie Live")
    parser.add_argument("--username", dest="username", required=True, help="Live username")
    parser.add_argument("--password", dest="password", required=True, help="Live password")
    parser.add_argument(
        "--rest_input", dest="rest_input", required=True, help="Path of the rest input integration"
    )
    parser.add_argument("--user_id", dest="user_id", required=True, help="Live user id")
    parser.add_argument("--room_id", dest="room_id", required=True, help="Target room id")

    return parser.parse_args(argv[1:])


def build_settings(args):
    return {
        "output": {
            "author": {"id": args.user_id, "name": "🤖  Messages bot "},
            "room": {"id": args.room_id},
        },
        "live": {
            "url": args.live_url,
            "rest_input": args.rest_input,
            "username": args.username,
            "password": args.password,
            "user_id": args.user_id,
        },
    }


if __name__ == "__main__":
    """
    Connects to a live instance and watches every query which is started
    For each query, sends a message to one of the messenger's rooms
    """
    args = parse_arguments(sys.argv)
    settings = build_settings(args)

    example_query = "__queries action:start => expression, description"
    span = f"last 60 seconds"

    @on_event(example_query, settings, span=span, timeout=120)
    def handle_events(event):
        event_data = event.get("data", {})
        content = event_data.get("content", {})
        template = "New query: '{}'"
        for item in content:
            message = template.format(item["expression"])
            print(message)
            messenger.send_message(
                message, timestamp=item["timestamp"], process_settings=settings
            )

        return

    handle_events()
```

More examples can be found on the folder `docs/examples`.

## Development

This project uses [black](https://github.com/psf/black) and [pre-commit](https://pre-commit.com/)

### Running the Tests

If you installled `dev-requirements.txt` you already have `pytest` installed.
Then just `cd` to the `tests` directory and run `pytest`.

### Publishing to pypi

```
# Build the packages
$ python setup.py egg_info sdist

# Validate the package
$ twine check dist/*

# Upload the package
$ twine upload dist/*
```


