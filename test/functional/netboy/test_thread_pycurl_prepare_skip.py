import logging

from wrap.show import show

from netboy.netboy import NetBoy
from netboy.util.setup_log import setup_log


def prepare_it(data):
    return {'skip': 1, 'update': 1}
    # return


@show(name='netboy')
def test_it(data):
    setup_log('netboy')
    boy = NetBoy()
    boy.use_spider(
        'pycurl'
    ).use_filter(
        ['url', 'title', 'effect']
    ).use_workers().use_prepares([
        'test.functional.netboy.test_thread_pycurl_prepare_skip.prepare_it'
    ]).use_mode('thread').use_timeout(10, 5, 5, 5).use_workers(8, 2, 2)#.use_queue('worker')
    resp = boy.run(data)
    return resp


if __name__ == '__main__':
    data = [
        'http://www.lhsajj.com', #extrem slow
        'http://www.bing.com',
        'http://www.hbcs.gov.cn',
        'http://www.hnxcdj.com',
        'http://www.ryzj.gov.cn',
        'http://www.nysylj.com',
        'http://www.nyszglc.com',
        'http://www.ayjtj.gov.cn',
        'http://www.hbxgtzyj.gov.cn',
        'http://www.hnrdia.com',
        'http://www.zmdggjy.com',
        'http://www.xyxgtzyj.gov.cn',
        'http://www.xxdsyjs.com',
        'http://www.xixiaagri.gov.cn',
        'http://www.xmdj.gov.cn',
        'http://www.xysrsjzlzpksbmw.gov.cn',
        # {'url': 'http://www.xysrsjzlzpksbmw.gov.cn',
        #  'effect': 'http://www.xysrsjzlzpksbmw.gov.cn/webregister/index.aspx'}
    ]
    resp = test_it(data)
    print(resp)
