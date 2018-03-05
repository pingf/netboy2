from copy import copy
from worker.worker import Worker

from netboy.asyncio_pycurl.curl_one import work as curl_work


class NetBoy:
    def __init__(self, info=None):
        self.worker = Worker(mode='celery')
        self.info = info if info else {}
        self.info['dummy'] = 'netboy.celery.tasks.dummy'
        self.info['log'] = 'netboy'

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

    def use_auth(self, user, password, group='default'):
        self.info['auth'] = {
            'user': user,
            'password': password,
            'group': group
        }
        return self

    def use_info(self, info):
        self.info = info
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
        return self

    def use_logger(self, logger):
        self.info['log'] = logger
        return self

    def run(self, data):
        # 'celery_max_workers': 4,
        # 'celery_chunk_size': 10,
        # 'chunk_size': 5,
        size = len(data)

        resp = self.worker.work(data, self.info)
        return resp

    def run_remote(self, url, data, callback_data=None):
        triggers = self.info.get('triggers')
        trigger_payload = {'trigger': 'netboy.support.triggers.post_it'}
        if callback_data:
            trigger_payload.update(callback_data)
            if triggers:
                self.info['triggers'].append(trigger_payload)
            else:
                self.info['triggers'] = [trigger_payload]

        payload = {
            'url': url,
            'method': 'post',
            'postfields': {
                'info': copy(self.info),
                'data': data
            }
        }

        resp = curl_work(payload, logger='netboy')
        return resp

    def register_remote(self, url, user, password, group='default'):
        payload = {
            'url': url,
            'method': 'post',
            'postfields': {
                'user': user,
                'password': password,
                'group': group
            }
        }

        resp = curl_work(payload, logger='netboy')
        return resp


if __name__ == '__main__':
    data = [
               # 'http://www.xixiaagri.gov.cn/'
               # 'http://www.xxdsyjs.com'
               # 'http://www.puyangdangshi.com'



               # 'http://www.csdn.net',
               'http://www.bing.com',
               # 'http://www.douban.com',
               # 'http://www.qxjtzf.com',
               # 'http://www.lyzbj.org.cn',
               # 'http://www.hnhxrs.com',
               # 'http://www.puyangdangshi.com',
               # 'http://www.bfhbj.com',
               # 'http://www.xxlyj.cn',
               # 'http://www.xcsnks.cn',
               # 'http://www.xcswmw.cn',
               # 'http://www.xcsqxj.com',
               # 'http://www.hnpopss.gov.cn',
               # 'http://www.lyjtj.com',
               # 'http://www.rndj.com',
               # 'http://www.nxzj.com.cn',
               # 'http://www.ycxyw.gov.cn',
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
    # print(resp)
