import logging
from time import sleep

from wrap.show import show

from netboy.netboy import NetBoy
from netboy.util.setup_log import setup_log

from bs4 import BeautifulSoup


def trig_sub(payload, response):
    data = response.get('data')
    soup = BeautifulSoup(data, 'html.parser')
    aa = soup.select('h3 a')
    aaa = [e['href'] for e in aa]
    boy = NetBoy()
    boy.use_spider(
        'pycurl'
    ).use_filter(
        ['effect']
    ).use_mode('thread').use_timeout(10, 5, 5, 5).use_workers(4, 5, 5)
    boy.info['maxredirs'] = 2
    resps = boy.run(aaa)
    urls = [e['effect'] if e.get('state') == 'normal' else 'error' for resp in resps for e in resp]

    response.update({'urls': urls})
    return response


def trig_print(payload, response):
    log = payload.get('log')
    log = logging.getLogger(log)
    log.critical(str(response.get('urls')))


@show(name='netboy')
def test_it(data):
    setup_log('netboy')
    boy = NetBoy()
    boy.use_spider(
        'pycurl'
    ).use_filter(
        ['url', 'effect', 'title', 'charset']
    ).use_mode('process').use_timeout(10, 5, 5, 5).use_workers(4, 2, 2)
    resp = boy.run(data)
    return resp


if __name__ == '__main__':
    data = [
        'http://www.sqlyzx.gov.cn',
    ]
    resp = test_it(data)
    # print(resp)
