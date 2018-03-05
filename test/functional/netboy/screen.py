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
    ).use_workers().use_triggers([
        'test.functional.netboy.screen.print_screen'
    ])
    resp = boy.run(data)
    # print(resp[0].get('screen')[:100])
