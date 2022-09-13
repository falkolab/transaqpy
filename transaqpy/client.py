import logging
import types
from dataclasses import dataclass
from typing import Union, cast, Callable, Type
from transaqpy import commands, TransaqException
from transaqpy.connector import TransaqConnector
from transaqpy.structures import CmdResult, translate_to_object, Error, \
    TimeDiffResult, TransaqMessage, ConnectorVersion, ServerStatus
from transaqpy.utils import encoding, CommandMaker

logger = logging.getLogger(__name__)


class TransaqClientException(TransaqException):
    pass


class UnableToConnectTransaqClientException(TransaqClientException):
    pass


@dataclass(frozen=True)
class UnableToSendCommand(TransaqClientException):
    message = None
    command = None

def make_command_method(client, command_factory):
    def wrapper(*args, **kwargs):
        cmd = command_factory(*args, **kwargs)
        return client.send_command(cmd)
    setattr(client, command_factory.__name__, wrapper)
    return getattr(client, command_factory.__name__)


class TransaqClient:
    # should be none to detect first connect
    _connected = None
    _recover = False
    _connection_error = None
    _connected_blocker = False
    _can_disconnect = False
    _connector_initialized = False

    def __init__(self, message_handler: Callable, connector: TransaqConnector = None):
        self._connector = connector
        self._connector.callback = self.handle_message
        self._handler = message_handler

    def __getattr__(self, name):
        try:
            command_factory = getattr(commands, name)
            if not isinstance(command_factory, types.FunctionType) or name.startswith('_'):
                raise AttributeError
            return make_command_method(self, command_factory)
        except AttributeError:
            pass
        err = "'%s' object has no attribute '%s'"
        raise AttributeError(err % (self.__class__.__name__, name))

    @property
    def is_online(self):
        return self._connected and not self._recover

    @property
    def is_connected(self):
        return self._connected

    @property
    def is_recovering(self):
        return self._recover

    @property
    def is_connection_error(self):
        return self._connection_error is not None

    def get_connection_error(self):
        return self._connection_error

    def connect(self, host, login, password, port, **kwargs) -> Union[bool, None]:
        # deferred initialization
        if not self._connector_initialized:
            self._connector.initialize()
        if self._connected_blocker:
            logger.warning('You should disconnect before!')
            return False
        response = self.send_command(commands.connect(host, login, password, port, **kwargs))
        # if not response.success:
        #     error = response.text if isinstance(response, Error) else 'Unable to connect'
        #     raise UnableToConnectTransaqClientException(error)
        if not response.success:
            logger.warning(response.text)
            if response.text == 'Соединение уже установлено...':
                self._connected_blocker = True
                self._can_disconnect = True
                logger.warning(response.text)
                logger.warning('Reconnect ...')
                self.disconnect()
                return self.connect(host, login, password, port, **kwargs)
        self._connected_blocker = response.success
        return response.success

    def disconnect(self) -> Union[bool, None]:
        if not self._can_disconnect:
            return None
        if not self._connected_blocker:
            logger.warning('You should connect before!')
            return False
        # if self.is_connected:
            # Если в процессе работы коннектора подключение к серверу будет потеряно
            # (при этом приходит структура <server_status connected=false/>),
            # то вызов команды disconnect перед новым подключением с помощью команды connect - не требуется.
        response = self.send_command(
            CommandMaker("disconnect")
        )
        if not response.success:
            logger.warning("Can't disconnect because: %s", response.text)
        self._can_disconnect = not response.success
        self._connected_blocker = not response.success
        return response.success

    def __del__(self):
        self.disconnect()
        self._connector.release()
        self._connector_initialized = False

    def send_command(self, cmd: CommandMaker, result_parser: Type[TransaqMessage] = CmdResult) -> \
            Union[Error, TransaqMessage]:
        command_str: str = cmd.encode()
        logger.debug('Send command: %s', command_str)
        result = self._connector.send_command(command_str)
        logger.debug('Result: %s', result)
        error = Error.parse(result)
        if error and error.text:
            raise TransaqClientException(error.text.encode(encoding))
        else:
            return result_parser.parse(result)

    def handle_message(self, message: str):
        transaq_message = translate_to_object(message)
        if transaq_message is None:
            raise TransaqClientException('Unsupported XML message')
        if isinstance(transaq_message, ServerStatus):
            self._handle_status(transaq_message)
        self._handler(transaq_message)

    def _handle_status(self, status):
        self._status_received = True
        if status.is_error:
            self._can_disconnect = False
            self._connected = False
            self._recover = False
            self._connection_error = status.get_error()
        else:
            self._can_disconnect = True
            self._connected = status.is_connected
            self._recover = status.is_recover
            self._connection_error = None

    def request_server_status(self):
        return self.send_command(CommandMaker('server_status'))

    def get_server_time_difference(self) -> TimeDiffResult:
        return self.send_command(CommandMaker('get_servtime_difference'), TimeDiffResult)

    def get_version(self) -> ConnectorVersion:
        return cast(ConnectorVersion, self.send_command(CommandMaker('get_connector_version')))

    def change_pass(self, old_password: str, new_password: str):
        return self.send_command(CommandMaker('change_pass', oldpass=old_password, newpass=new_password))
