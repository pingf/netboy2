
from wrap.show import show

from netboy.netboy import NetBoy
from netboy.util.setup_log import setup_log


def trig_it(payload, response):
    print(response)


@show(name='netboy')
def test_it(data):
    setup_log('netboy')
    boy = NetBoy()
    boy.use_spider(
        'pycurl'
    ).use_filter(
        ['url', 'title', 'effect']
    ).use_triggers([
        'test.functional.netboy.test_thread_pycurl_basic.trig_it'
    ]).use_mode('thread').use_timeout(10, 5, 5, 5).use_workers(4, 2, 2)
    resp = boy.run(data)
    return resp


if __name__ == '__main__':
    data = [
        'http://www.bing.com',
        'http://www.douban.com',
    ]
    resp = test_it(data)
    print(resp)
