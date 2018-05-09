import base64
import logging

from netboy.netboy import NetBoy
from netboy.util.setup_log import setup_log


def print_screen(payload, response):
    log_name = payload.get('log')
    log = logging.getLogger(log_name)
    if response.get('screen'):
        print(response.get('title'))
        screen = response['screen']
        screen_100 = screen[:100]
        log.info('screen:' + screen_100)
        url = response.get('url')
        if url.startswith('http://'):
            url = url[7:]
        if url.startswith('https://'):
            url = url[8:]

        # with open(url+'.png', 'wb') as f:
        from PIL import Image
        import io
        data = base64.decodebytes(screen.encode('utf8'))
        image = Image.open(io.BytesIO(data))
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")

        image.save(url+'.jpg', 'JPEG', dpi=[300,300], quality=60)
    else:
        print(response)


if __name__ == '__main__':
    setup_log('netboy')
    data = [
        "http://172.30.0.3:9992",
        "http://ip.cn",
        "http://www.cnbeta.com",

        "http://www.hxsjjq.gov.cn",
        "http://www.douban.com"
               # "http://www.bing.com",
               # "http://www.hbcs.gov.cn",
               # "http://www.hnxcdj.com",
               # "http://www.ryzj.gov.cn",
               # "http://www.lhsajj.com",
               # "http://www.nysylj.com",
               # "http://www.nyszglc.com",
               # "http://www.ayjtj.gov.cn",
               # "http://www.hbxgtzyj.gov.cn",
               # "http://www.hnrdia.com",
               # "http://www.zmdggjy.com",
               # "http://www.xyxgtzyj.gov.cn",
               # "http://www.xxdsyjs.com",
               # "http://www.xixiaagri.gov.cn",
               # "http://www.xmdj.gov.cn",
               # "http://www.xysrsjzlzpksbmw.gov.cn",
           ] * 1
    # boy = NetBoy({'mode': 'coroutine'})
    # boy = NetBoy({'mode':'process'})
    boy = NetBoy()
    boy.use_queue(
        'worker'
    ).use_spider(
        'chrome'
    ).use_filter(
        ['url', 'title', 'screen']
    ).use_workers().use_triggers([
        'test.functional.netboy.screen.print_screen'
    # ]).use_mode('celery')
    ]).use_mode('thread')#.use_socks5_proxy('127.0.0.1:1082')
    resp = boy.run(data)
    # print(resp[0].get('screen')[:100])
