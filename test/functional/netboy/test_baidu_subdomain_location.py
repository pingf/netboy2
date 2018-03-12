import logging

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
        ['header']
    ).use_mode('thread').use_timeout(10, 5, 5, 5).use_workers(8, 2, 2)
    boy.info['maxredirs'] = 1
    boy.info['followlocation'] = 0
    urls = []
    resps = boy.run(aaa)
    for resp in resps:
        for r in resp:
            content = r['header']['content']
            for c in content:
                if c.get('location'):
                    urls.append(c.get('location')[0])
    response.update({'urls': urls})
    return response


def trig_print(payload, response):
    log = payload.get('log')
    log = logging.getLogger(log)
    log.critical(str(response.get('urls')))


def final(data, info):
    print('done')
    return 'final'


@show(name='netboy')
def test_it(data):
    setup_log('netboy')
    boy = NetBoy()
    boy.use_spider(
        'pycurl'
    ).use_filter(
        ['url', 'title', 'effect', 'data']
    ).use_triggers([
        'test.functional.netboy.test_baidu_subdomain_location.trig_sub',
        'test.functional.netboy.test_baidu_subdomain_location.trig_print',
    ]
    ).use_mode(
        'celery'
    ).use_timeout(10, 5, 5, 5).use_workers(8, 2, 2).use_queue(
        'worker'
    ).use_final('test.functional.netboy.test_baidu_subdomain_location.final')
    boy.info['job_id'] = 'test'
    resp = boy.run(data)
    return resp


if __name__ == '__main__':
    data = [
        'http://www.baidu.com/s?wd=site:{douban.com}&pn=0&rn=10',
        # 'http://www.baidu.com/s?wd=site:{douban.com}&pn=10&rn=10',
        # 'http://www.baidu.com/s?wd=site:{douban.com}&pn=20&rn=10',
        # 'http://www.baidu.com/s?wd=site:{douban.com}&pn=30&rn=10',
        # 'http://www.baidu.com/s?wd=site:{douban.com}&pn=40&rn=10',
        # 'http://www.baidu.com/s?wd=site:{movie.douban.com}&pn=0&rn=10',
        # 'http://www.baidu.com/s?wd=site:{movie.douban.com}&pn=10&rn=10',
        # 'http://www.baidu.com/s?wd=site:{movie.douban.com}&pn=20&rn=10',
        # 'http://www.baidu.com/s?wd=site:{movie.douban.com}&pn=30&rn=10',
        # 'http://www.baidu.com/s?wd=site:{movie.douban.com}&pn=40&rn=10',
        # 'http://www.baidu.com/s?wd=site:{www.douban.com}&pn=0&rn=10',
        # 'http://www.baidu.com/s?wd=site:{www.douban.com}&pn=10&rn=10',
        # 'http://www.baidu.com/s?wd=site:{www.douban.com}&pn=20&rn=10',
        # 'http://www.baidu.com/s?wd=site:{www.douban.com}&pn=30&rn=10',
        # 'http://www.baidu.com/s?wd=site:{www.douban.com}&pn=40&rn=10',
        # 'http://www.baidu.com/s?wd=site:{www.csdn.net}&pn=0&rn=10',
        # 'http://www.baidu.com/s?wd=site:{www.csdn.net}&pn=10&rn=10',
        # 'http://www.baidu.com/s?wd=site:{www.csdn.net}&pn=20&rn=10',
        # 'http://www.baidu.com/s?wd=site:{www.csdn.net}&pn=30&rn=10',
        # 'http://www.baidu.com/s?wd=site:{www.csdn.net}&pn=40&rn=10',
        # 'http://www.baidu.com/s?wd=site:{www.sina.com.cn}&pn=0&rn=10',
        # 'http://www.baidu.com/s?wd=site:{www.sina.com.cn}&pn=10&rn=10',
        # 'http://www.baidu.com/s?wd=site:{www.sina.com.cn}&pn=20&rn=10',
        # 'http://www.baidu.com/s?wd=site:{www.sina.com.cn}&pn=30&rn=10',
        # 'http://www.baidu.com/s?wd=site:{www.sina.com.cn}&pn=40&rn=10',

        # 'http://www.baidu.com/link?url=N_mqKchTzfgXdAhReoECh1TKOg8_X6bNoRzgwjKaA2Dl2DONz8Q_o2dhg-OaTS21PJ6w7enRxpEHSwX0yRYT9a'
    ]
    resp = test_it(data)
    # print(resp)
