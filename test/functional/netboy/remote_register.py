import logging

from netboy.netboy import NetBoy
from netboy.util.setup_log import setup_log


def print_screen(payload, reponse):
    log_name = payload.get('log')
    log = logging.getLogger(log_name)
    screen_100 = reponse['screen'][:100]
    log.info(screen_100)


if __name__ == '__main__':
    setup_log('netboy')
    boy = NetBoy()
    resp = boy.register_remote('127.0.0.1:8080/register', user='dameng', password='hello')
