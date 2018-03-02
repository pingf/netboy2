import socket
import sys

import os
from celery import Celery
from logcc.logcc import LogCC
from termcc.cc import cc
from termcc.core import red

from netboy.util.setup_log import setup_log


# app = Celery('netboy', include=[
#     'netboy.celery.tasks'
# ])

class BasicConfig:
    def __init__(self):
        self.enable_utc = True
        self.timezone = 'UTC'  # 'Europe/London'
        self.task_serializer = 'pickle'  # 'msgpack'
        self.result_serializer = 'json'
        self.accept_content = ['json', 'msgpack', 'pickle']
        self.timezone = 'UTC'
        self.enable_utc = True
        self.chord_propagates = False
        self.task_send_sent_event = True
        self.worker_hijack_root_logger = False

class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            setup_log('netboy')
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class App(metaclass=Singleton):
    def __init__(self, mode='normal'):
        self.app = Celery('netboy')
        self.app.config_from_object(BasicConfig())
        self.app.config_from_object('celeryconfig')

