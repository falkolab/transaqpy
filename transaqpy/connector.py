from abc import ABCMeta, abstractmethod
from typing import Callable
from transaqpy import TransaqException


class TransaqConnectorException(TransaqException):
    pass


class TransaqConnector:
    __metaclass__ = ABCMeta
    _callback: Callable = None

    def __init__(self, callback: Callable = None):
        self._callback = callback

    def __enter__(self):
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.release()

    def __del__(self):
        self.release()

    def _set_callback(self, func: Callable):
        self._callback = func

    callback = property(fset=_set_callback)

    @abstractmethod
    def initialize(self, *args, **kw) -> bool:
        pass

    @abstractmethod
    def release(self):
        pass

    @abstractmethod
    def send_command(self, cmd) -> str:
        pass
