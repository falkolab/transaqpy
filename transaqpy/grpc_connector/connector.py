from queue import Queue

import grpc
from threading import Thread, Event
import logging
from typing import Iterator

from transaqpy.connector import TransaqConnector
from transaqpy.grpc_connector.proto import connect_pb2_grpc, connect_pb2
logger = logging.getLogger(__name__)


class GRPCTransaqConnector(TransaqConnector):

    _channel = None
    _stub = None
    _consumer_feature = None
    _queue = None

    def __init__(self, server='127.0.0.1:50051', callback=None):
        super().__init__(callback)
        self._channel = grpc.insecure_channel(server)
        self._stub = connect_pb2_grpc.ConnectServiceStub(self._channel)
        self._peer_responded = Event()
        self._consumer_feature = None
        self._queue = Queue(-1)

    def send_command(self, cmd) -> str:
        request = connect_pb2.SendCommandRequest(message=cmd)
        response = self._stub.SendCommand(request)
        return response.message if hasattr(response, "message") else None

    def initialize(self):
        request = connect_pb2.DataRequest()
        response_iterator = self._stub.FetchResponseData(request)
        worker = Thread(target=self._response_watcher, daemon=True, args=(response_iterator,))
        worker.start()
        message_processor = Thread(target=self._process_messages, daemon=True)
        message_processor.start()

    def release(self):
        if self._consumer_feature:
            self._consumer_feature.cancel()
            self._consumer_feature = None

    def _process_messages(self):
        while True:
            message = self._queue.get()
            if self._callback:
                self._callback(message)
            self._queue.task_done()

    def _response_watcher(
            self,
            response_iterator: Iterator[connect_pb2.SendCommandResponse]) -> None:
        try:
            for response in response_iterator:
                if hasattr(response, "message"):
                    self._queue.put(response.message)
                else:
                    raise RuntimeError(
                        "Received SendCommandResponse without message"
                    )
        except Exception as e:
            logger.error("Error on input message loop: %s", e)
            raise
