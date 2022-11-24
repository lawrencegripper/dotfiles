#!/usr/bin/env python3

import json
import socket
from typing import TextIO, Sequence
from enum import IntEnum
from typing import Sequence, Optional, Mapping, Tuple
import io


class Urgency(IntEnum):
    LOW = 0
    NORMAL = 1
    CRITICAL = 2


class CloseReason(IntEnum):
    EXPIRED = 1
    DISMISSED = 2
    CLOSED = 3
    RESERVED = 4

ROFICATION_UNIX_SOCK =  "/tmp/rofi_notification_daemon"


class NullTextIO(io.TextIOBase, TextIO):
    def write(self, s: str) -> int:
        return 0


nullio: TextIO = NullTextIO()


class Notification:
    def __init__(self) -> None:
        self.id: Optional[int] = None
        self.deadline: Optional[float] = None
        self.summary: Optional[str] = None
        self.body: Optional[str] = None
        self.application: Optional[str] = None
        self.icon: Optional[str] = None
        self.urgency: Urgency = Urgency.NORMAL
        self.actions: Sequence[str] = ()
        self.hints: Mapping[str, any] = {}
        self.timestamp = None

    def asdict(self) -> Mapping[str, any]:
        return {field: value for field, value in vars(self).items() if value is not None}

    @classmethod
    def make(cls, dct: Mapping[str, any]) -> 'Notification':
        notification: 'Notification' = cls()
        notification.id = dct.get('id')
        notification.deadline = dct.get('deadline')
        notification.summary = dct.get('summary')
        notification.body = dct.get('body')
        notification.application = dct.get('application')
        notification.icon = dct.get('icon')
        notification.urgency = Urgency(dct.get('urgency', Urgency.NORMAL))
        notification.actions = tuple(dct.get('actions', ()))
        notification.hints = dct.get('hints')
        notification.timestamp = dct.get('timestamp', '')
        return notification

class RoficationClient:
   def __init__(self, out: TextIO = nullio, unix_socket: str = ROFICATION_UNIX_SOCK):
       self._out: TextIO = out
       self._unix_socket: str = unix_socket

   def _client_socket(self) -> socket.socket:
       sck = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
       sck.connect(self._unix_socket)
       return sck

   def _send(self, command: str, arg: any) -> None:
       with self._client_socket() as sck:
           sck.send(bytes(f'{command}:{arg}\n', encoding='utf-8'))

   def count(self) -> (Tuple[int, int]):
       with self._client_socket() as sck:
           sck.send(b'num\n')
           data = sck.recv(32).decode('utf-8')
           return (int(x) for x in data.split(',', 2))

   def delete(self, nid: int) -> None:
       self._send('del', nid)

   def delete_multi(self, ids: str) -> None:
           self._send('delm', ids)

   def delete_all(self, application: str) -> None:
       self._send('dela', application)

   def list(self) -> Sequence[Notification]:
       with self._client_socket() as sck:
           sck.send(b'list\n')
           with sck.makefile(mode='r', encoding='utf-8') as fp:
               return json.load(fp, object_hook=Notification.make)

   def see(self, nid: int) -> None:
       self._send('see', nid)

client: RoficationClient = RoficationClient()

print('hi')
print(client.list[0])