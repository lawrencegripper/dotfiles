#!/usr/bin/env python3

import json
import socket
from typing import TextIO, Sequence
from enum import IntEnum, Enum
from typing import Sequence, Optional, Mapping, Tuple
import io
from blinkstick import blinkstick
import dbm
import os

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

notificationsClient: RoficationClient = RoficationClient()
blinkStickClient: blinkstick.BlinkStick = blinkstick.find_first()
storage = dbm.open('/tmp/notifications_store', 'c')

class Color(Enum):
    PURPLE = 6
    RED = 5
    ORANGE = 4
    YELLOW = 3
    BLUE = 1
    OFF = 0

color_to_set: Color = Color.OFF

if 'last_color' not in storage:
    storage['last_color'] = Color.OFF.name

if 'last_count' not in storage:
    storage['last_count'] = "0"


def set_if_higher(color: Color):
    global color_to_set
    if color.value > color_to_set.value:
        color_to_set = color

notifications: enumerate = enumerate(notificationsClient.list())

count = 0
for index, notification in notifications:
    count += 1
    color_to_set = Color.BLUE
    if os.environ.get('DEBUG', False):
        print(f'App:     {notification.application}')
        print(f'Summary: {notification.summary}')
        print(f'Body:    {notification.body}')
        print("----")
        
    # Set priorities
    if notification.application == "Signal":
        set_if_higher(Color.ORANGE)
        if notification.summary == "Minty RB":
            set_if_higher(Color.PURPLE)
    if notification.application == "Morgen":
        set_if_higher(Color.RED)
    if notification.application == "gitify":
        set_if_higher(Color.BLUE)
    
    # Clear out stuff
    if notification.application == "Stretchly":
        notificationsClient.delete(notification.id)
        count -= 1
    if notification.application == "NetworkManager":
        notificationsClient.delete(notification.id)
        count -= 1

    # Slack triage
    if notification.application == "Firefox" and notification.summary.startswith("New message"):
        # Chatop response lower priority
        if "-ops" in notification.summary:
            set_if_higher(Color.BLUE)
            continue
        elif "@lawrencegripper" in notification.body:
            set_if_higher(Color.RED)
        else:
            notificationsClient.delete(notification.id)
        # Default for slack
        set_if_higher(Color.YELLOW)
        # It's a DM from someone
        if "#" not in notification.summary:
            set_if_higher(Color.ORANGE)
    
    set_if_higher(Color.BLUE)

if count == 0:
    color_to_set = Color.OFF

last_color: Color = Color[bytes.decode(storage["last_color"])]
last_count: int= int(bytes.decode(storage['last_count']))
    
if color_to_set != Color.OFF and (last_color != color_to_set or last_count > count):
    blinkStickClient.blink(name= color_to_set.name.lower(), repeats=7, delay=1000)

blinkStickClient.set_color(name = color_to_set.name.lower())

storage["last_color"] = color_to_set.name
storage["last_count"] = str(count)

color_hex = ""
match color_to_set:
    case Color.RED: color_hex = "#ff3333"
    case Color.ORANGE:  color_hex = "#ffb31a"
    case Color.YELLOW:  color_hex = "#ffff1a"
    case Color.BLUE:  color_hex = "#66b3ff"
    case Color.OFF:  color_hex = "#e6e6e6"

print("%{F" + color_hex + "} " + str(count))
