# Интеграция для Transaq Connector на Python

**Важно!** Модуль находится на стадии тестирования. Используйте с осторожностью на свой страх и риск.

Этот проект в текущем виде не использует напрямую transaq connect библиотеку. Изначально разрабатывался для запуска 
в Docker контейнере, но при желании можно добавить нативный коннектор, это не должно быть сложно.

Т.е. для работы необходимо запустить контейнер из проекта [txmlconnector](https://github.com/kmlebedev/txmlconnector)

## Пример использования
```python
import os
from transaqpy.client import TransaqClient
from transaqpy.structures import TransaqMessage
from transaqpy.grpc_connector.connector import GRPCTransaqConnector
from transaqpy import commands

def receiver(self, message: TransaqMessage):
    print('Received message: ', message.ROOT_NAME)
    print('Receiver: ', message.__repr__())
        
connector = GRPCTransaqConnector(os.environ['GRPC_SERVER'])
client = TransaqClient(receiver, connector)
client.connect(...)
client.send_command(commands.get_sec_info('TQBR', 'GAZP'))
```