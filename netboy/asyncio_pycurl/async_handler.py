import logging
import random
import pycurl

import asyncio
from logcc.logcc import LogCC
from termcc.cc import cc
from termcc.core import red
from worker.worker import Worker

from netboy.asyncio_pycurl.curl_factory import CurlFactory


async def curl_handler(data, info):
    factory = CurlFactory(data, info)
    factory.allocate()
    r = await factory.run()
    return r













if __name__ == '__main__':
    try:
        import signal
        from signal import SIGPIPE, SIG_IGN

        signal.signal(signal.SIGPIPE, signal.SIG_IGN)
    except ImportError:
        pass

    l = LogCC(name='worker')
    l.update_color_formatter('name', 'DEBUG', red())
    l.update_color_formatter('name', 'INFO', cc(':blue::man::red::woman:'))

    data = [
        # 'http://www.baidu.com',
        # 'http://www.douban.com',
        # 'http://www.bing.com',
        # 'http://www.csdn.net',
        'http://www.yahoo.com',
        # 'http://www.zhihu.com',
        # 'http://www.qxjtzf.com',
        # 'http://www.lyzbj.org.cn',
        # 'http://www.hnhxrs.com',
        # 'http://www.puyangdangshi.com',
        # 'http://www.xxlyj.cn',
        # 'http://www.xcsnks.cn',
        # 'http://www.xcswmw.cn',
        # 'http://www.xcsqxj.com',
        # 'http://www.hnpopss.gov.cn',
        # 'http://www.lyjtj.com',
        # 'http://www.rndj.com',
        # 'http://www.nxzj.com.cn',

    ]
    info = {
        'worker': 'netboy.asyncio_pycurl.async_handler.curl_handler',
        'chunk_size': 5,
    }

    worker = Worker(mode='celery')
    resp = worker.work(data, info)
    print(resp)
