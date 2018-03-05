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
    data = [
               'http://www.bing.com',
           ] * 1
    boy = NetBoy()
    boy.use_queue(
        'worker'
    ).use_spider(
        'chrome'
    ).use_filter(
        ['url', 'title', 'screen']
    ).use_auth('dameng', 'hello')
    resp = boy.run_remote('127.0.0.1:8080/run', data,
                          callback_data={'url': '127.0.0.1:8080/post', 'hello': 'world'})
    # print(resp)
    # print(resp[0].get('screen')[:100])
