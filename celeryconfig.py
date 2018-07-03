import os
import socket

ENV_IP = os.environ.get('ENV_IP', '127.0.0.1')
ip = ENV_IP
if '.' not in ip:
    ip = [(s.connect(('223.5.5.5', 53)), s.getsockname()[0], s.close()) for s in
          [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]

broker_url = os.environ.get('CELERY_BROKER_URL', 'amqp://dameng:hello@' + ip + '/netboy')
result_backend = os.environ.get('CELERY_RESULT_URL', 'redis://:hello@' + ip + ':6379/2')


# worker_prefetch_multiplier = 1
# worker_concurrency = 4
# worker_hijack_root_logger = False
