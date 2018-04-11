import base64
import logging

from netboy.netboy import NetBoy
from netboy.util.setup_log import setup_log


def print_screen(payload, response):
    print('.'*200)
    log_name = payload.get('log')
    log = logging.getLogger(log_name)
    if response.get('screen'):
        print('title', response.get('title'))
        # print('data', response.get('data'))
        screen = response['screen']
        # with open('test.png', 'wb') as f:
        #     f.write(screen)

        screen_100 = screen[:100]
        log.info('screen:' + screen_100)
    else:
        print(response)


if __name__ == '__main__':
    print('haha')
    setup_log('netboy')
    data = [
        "http://ssqgz.30edu.com.cn/",

        "http://rneg.30edu.com.cn/",
        "http://tkxjytyj.30edu.com.cn"
           ] * 1
    # boy = NetBoy({'mode': 'coroutine'})
    # boy = NetBoy({'mode':'process'})
    boy = NetBoy()
    boy.use_queue(
        'worker'
    ).use_spider(
        'chrome'
    ).use_filter(
        ['url', 'title', 'screen', 'data']
    ).use_workers().use_triggers([
        'test.functional.netboy.test_chrome_edu30.print_screen'
    # ]).use_mode('celery')
    ]).use_mode('thread').use_timeout(30, 30, 30, 30)
    resp = boy.run(data)
    # print(resp[0].get('screen')[:100])
