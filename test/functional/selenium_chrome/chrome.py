from logcc.logcc import LogCC
from termcc.cc import cc
from termcc.core import red
from worker.worker import Worker

if __name__ == '__main__':
    l = LogCC(name='worker')
    l.update_color_formatter('name', 'DEBUG', red())
    l.update_color_formatter('name', 'INFO', cc(':blue::man::red::woman:'))
    data = [
               # 'http://www.xixiaagri.gov.cn/'
               # 'http://www.xxdsyjs.com'
               # 'http://www.puyangdangshi.com'



               # 'http://www.csdn.net',

               # {'url':'http://www.baidu.com', 'filter': ['data']},
               'http://www.baidu.com',
               # 'http://www.douban.com',
               # 'http://www.bing.com',
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
    info = {
        'proxytype': 'socks5',
        'proxy': '127.0.0.1',
        'proxyport': 1082,
        'celery_worker': 'netboy.celery.tasks.thread_worker',
        'worker': 'netboy.celery.tasks.thread_worker_do_crawl',
        'celery_max_workers': 4,
        'celery_chunk_size': 2,
        'chunk_size': 2,
        'queue': 'worker',
        'dummy': 'netboy.celery.tasks.dummy',
        'filter': ['url', 'title'],
        'triggers': [
            {'hello': 'world'},
            {'hello2': 'world2'},
            {'trigger': 'netboy.support.trigger.trig_it'},
        ],
        'analysers': ['netboy.support.analysers.analyse_it']
    }
    worker = Worker(mode='celery')
    resp = worker.work(data, info)
    print(resp)
