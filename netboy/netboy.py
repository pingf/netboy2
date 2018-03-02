from logcc.logcc import LogCC
from termcc.cc import cc
from termcc.core import red
from worker.worker import Worker

from netboy.util.setup_log import setup_log


class NetBoy:
    def __init__(self, info=None):
        self.worker = Worker(mode='celery')
        self.info = info if info else {}
        self.info['dummy'] = 'netboy.celery.tasks.dummy'


    def use_socks5_proxy(self, proxy):
        p = proxy.split(':')
        self.info['proxytype'] = 'socks5'
        self.info['proxy'] = p[0]
        self.info['proxyport'] = int(p[1])
        return self

    def use_queue(self, queue):
        self.info['queue'] = queue
        return self

    def use_logger(self, log_name):
        self.info['log'] = log_name
        return self

    def use_filter(self, result_filter):
        self.info['filter'] = result_filter
        return self

    def use_triggers(self, triggers):
        self.info['triggers'] = triggers
        return self

    def use_analysers(self, analysers):
        self.info['analysers'] = analysers
        return self

    def use_spider(self, spider='pycurl'):
        if spider == 'pycurl':
            self.info['celery_worker'] = 'netboy.celery.tasks.coroutine_worker'
            self.info['worker'] = 'netboy.celery.tasks.coroutine_worker_do_crawl'
        elif spider == 'chrome':
            self.info['celery_worker'] = 'netboy.celery.tasks.thread_worker'
            self.info['worker'] = 'netboy.celery.tasks.thread_worker_do_crawl'
        return self

    def use_workers(self, workers=4, chunk_size1=40, chunk_size2=8):
        self.info['celery_max_workers'] = workers
        self.info['celery_chunk_size'] = chunk_size1
        self.info['chunk_size'] = chunk_size2

    def run(self, data):
        # 'celery_max_workers': 4,
        # 'celery_chunk_size': 10,
        # 'chunk_size': 5,
        size = len(data)

        resp = self.worker.work(data, self.info)
        return resp


if __name__ == '__main__':
    data = [
               # 'http://www.xixiaagri.gov.cn/'
               # 'http://www.xxdsyjs.com'
               # 'http://www.puyangdangshi.com'



               # 'http://www.csdn.net',
               'http://www.bing.com',
               'http://www.douban.com',
               'http://www.qxjtzf.com',
               'http://www.lyzbj.org.cn',
               'http://www.hnhxrs.com',
               'http://www.puyangdangshi.com',
               'http://www.bfhbj.com',
               'http://www.xxlyj.cn',
               'http://www.xcsnks.cn',
               'http://www.xcswmw.cn',
               'http://www.xcsqxj.com',
               'http://www.hnpopss.gov.cn',
               'http://www.lyjtj.com',
               'http://www.rndj.com',
               'http://www.nxzj.com.cn',
               'http://www.ycxyw.gov.cn',
               # 'http://www.hnyssw.gov.cn',
               # 'http://www.hbcs.gov.cn',
               # 'http://www.hnxcdj.com',
               # 'http://www.ryzj.gov.cn',
               # 'http://www.lhsajj.com',
               # 'http://www.nysylj.com',
               # 'http://www.nyszglc.com',
               # 'http://www.ayjtj.gov.cn',
               # 'http://www.hbxgtzyj.gov.cn',
               # 'http://www.hnrdia.com',
               # 'http://www.zmdggjy.com',
               # 'http://www.xyxgtzyj.gov.cn',
               # 'http://www.xxdsyjs.com',
               # 'http://www.xixiaagri.gov.cn',
               # 'http://www.xmdj.gov.cn',
               # 'http://www.xysrsjzlzpksbmw.gov.cn',

           ] * 1
    boy = NetBoy()
    boy.use_analysers([
        'netboy.support.analysers.analyse_it'
    ]).use_queue(
        'worker'
    ).use_spider(
        'pycurl'
    ).use_filter(['url', 'title']).use_workers()
    resp = boy.run(data)

    print(resp)
