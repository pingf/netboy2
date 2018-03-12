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
        ['url', 'title', 'effect', 'data']
    ).use_triggers([
        'test.functional.netboy.test_baidu_subdomain.trig_sub',
        'test.functional.netboy.test_baidu_subdomain.trig_print',
    ]
    ).use_mode('process').use_timeout(10, 5, 5, 5).use_workers(4, 2, 2)
    resp = boy.run(data)
    return resp


if __name__ == '__main__':
    data = [
        'http://www.baidu.com/s?wd=site:{www.douban.com}&pn=0&rn=10',
        'http://www.baidu.com/s?wd=site:{www.douban.com}&pn=10&rn=10',
        'http://www.baidu.com/s?wd=site:{www.douban.com}&pn=20&rn=10',
        'http://www.baidu.com/s?wd=site:{www.douban.com}&pn=30&rn=10',
        'http://www.baidu.com/s?wd=site:{www.douban.com}&pn=40&rn=10',
        'http://www.baidu.com/s?wd=site:{www.csdn.net}&pn=0&rn=10',
        'http://www.baidu.com/s?wd=site:{www.csdn.net}&pn=10&rn=10',
        'http://www.baidu.com/s?wd=site:{www.csdn.net}&pn=20&rn=10',
        'http://www.baidu.com/s?wd=site:{www.csdn.net}&pn=30&rn=10',
        'http://www.baidu.com/s?wd=site:{www.csdn.net}&pn=40&rn=10',
        # 'http://www.baidu.com/link?url=N_mqKchTzfgXdAhReoECh1TKOg8_X6bNoRzgwjKaA2Dl2DONz8Q_o2dhg-OaTS21PJ6w7enRxpEHSwX0yRYT9a'
    ]
    resp = test_it(data)
    # print(resp)
