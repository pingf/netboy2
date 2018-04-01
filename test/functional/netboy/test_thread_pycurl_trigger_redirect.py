import re
from wrap.show import show

from netboy.netboy import NetBoy
from netboy.util.setup_log import setup_log
from netboy.multi_pycurl.curl_one import work as curl_work


def trigger_it(payload, response):
    print('*' * 200)
    print(response.get('url'))
    data = response.get('data')
    # print(data[:40])
    # print(data)
    match = re.search('<script[^>]*>\s*document.location\s*=\s*\'([^<]+)\'\s*</script>', data)
    if match:

        text = match.group(1)
        raw_url = payload.get('url')
        url_prefix = raw_url if raw_url.endswith('/') else raw_url + '/'
        new_url = url_prefix + text
        print('new url:'+new_url)
        payload['effect'] = new_url
        response = curl_work(payload)
        response['update'] = True
        return response


def trigger_it2(payload, response):
    print('*' * 200)
    print(response.get('url'))
    data = response.get('data')
    print(data[:400])

@show(name='netboy')
def test_it(data):
    setup_log('netboy')
    boy = NetBoy()
    boy.use_spider(
        'pycurl'
    ).use_filter(
        ['url', 'title', 'effect', 'data']
    ).use_workers().use_triggers([
        'test.functional.netboy.test_thread_pycurl_trigger_redirect.trigger_it',
        'test.functional.netboy.test_thread_pycurl_trigger_redirect.trigger_it2'
    ]).use_mode('thread').use_timeout(15, 5)
    resp = boy.run(data)
    return resp


if __name__ == '__main__':
    data = [
        # 'http://www.bing.com',
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
        # {'url': 'http://www.xysrsjzlzpksbmw.gov.cn', 'effect': 'http://www.xysrsjzlzpksbmw.gov.cn/webregister/index.aspx'}
        'http://www.xysrsjzlzpksbmw.gov.cn'
    ]
    resp = test_it(data)
    # print(resp)
