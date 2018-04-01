import logging

from netboy.netboy import NetBoy
from netboy.util.setup_log import setup_log


def print_screen(payload, response):
    log_name = payload.get('log')
    log = logging.getLogger(log_name)
    if response.get('screen'):
        print(response.get('title'))
        screen_100 = response['screen'][:100]
        log.info('screen:' + screen_100)
    else:
        print(response)


if __name__ == '__main__':
    setup_log('netboy')
    data = [
               "http://www.bing.com",
               "http://www.hbcs.gov.cn",
               "http://www.hnxcdj.com",
               "http://www.ryzj.gov.cn",
               # "http://www.lhsajj.com",
               # "http://www.nysylj.com",
               # "http://www.nyszglc.com",
               # "http://www.ayjtj.gov.cn",
               # "http://www.hbxgtzyj.gov.cn",
               # "http://www.hnrdia.com",
               # "http://www.zmdggjy.com",
               # "http://www.xyxgtzyj.gov.cn",
               # "http://www.xxdsyjs.com",
               # "http://www.xixiaagri.gov.cn",
               # "http://www.xmdj.gov.cn",
               # "http://www.xysrsjzlzpksbmw.gov.cn",
           ] * 1
    # boy = NetBoy({'mode': 'coroutine'})
    # boy = NetBoy({'mode':'process'})
    boy = NetBoy()
    boy.use_queue(
        'worker'
    ).use_spider(
        'chrome'
    ).use_filter(
        ['url', 'title', 'screen']
    ).use_workers().use_triggers([
        'test.functional.netboy.screen.print_screen'
    # ]).use_mode('celery')
    ]).use_mode('thread')
    resp = boy.run(data)
    # print(resp[0].get('screen')[:100])
