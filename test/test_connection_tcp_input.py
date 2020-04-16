from testbase import *

import json
import multiprocessing as mp
import queue
import requests
import socket
import time

from unittest import mock

from live_client.connection import tcp_input
from mocks import *
from predicates import *
from utils import settings as S
from utils.micro_tcp import MicroTcpServer

SERVER_ADDR = ("127.0.0.1", 8889)
DEFAULT_SETTINGS = {"ip": SERVER_ADDR[0], "port": SERVER_ADDR[1]}


class TestSendEvent:
    def test_event_is_sent(self):
        server = MicroTcpServer(SERVER_ADDR)
        time.sleep(0.1)

        message = "!!Testando !!"
        tcp_input.send_event({"message": message}, DEFAULT_SETTINGS)

        try:
            message_back = json.loads(server.output_queue.get())
            server.close()
        except queue.Empty as e:
            message_back = None

        assert message_back["message"] == message

    def test_no_event_sent_if_no_message(self):
        server = MicroTcpServer(SERVER_ADDR)
        time.sleep(0.1)

        tcp_input.send_event({}, DEFAULT_SETTINGS)
        try:
            message = server.output_queue.get(True, 1)
            assert False  # If we are here the message has been sent
        except queue.Empty as e:
            server.close()

    def test_raises_on_invalid_settings(self):
        assert raises(KeyError, tcp_input.send_event, {"message": "_"}, {"ip": "127.0.0.1"})
        assert raises(KeyError, tcp_input.send_event, {"message": "_"}, {"port": 3210})
