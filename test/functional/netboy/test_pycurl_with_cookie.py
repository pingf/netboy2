import logging
from time import sleep

from wrap.show import show

from netboy.netboy import NetBoy
from netboy.util.setup_log import setup_log

from bs4 import BeautifulSoup


def trig_it(payload, response):
    print(response.keys())
    print(response.get('cookie'))
    return response




@show(name='netboy')
def test_it(data):
    setup_log('netboy')
    boy = NetBoy()
    boy.use_triggers(['test.functional.netboy.test_pycurl_with_cookie.trig_it'])
    boy.use_spider(
        'pycurl'
    ).use_filter(
        ['url', 'effect', 'title', 'cookie']
    ).use_mode('process').use_timeout(10, 5, 5, 5).use_workers(1,1,1)
    # boy.info['cookie'] = bytes('test=value',"utf8")
    boy.info['cookie'] = 't1=v1;t2=v2'.encode("utf8")
    resp = boy.run(data)
    return resp


if __name__ == '__main__':
    data = [
        'http://127.0.0.1:8080',
    ]
    resp = test_it(data)
    # print(resp)
