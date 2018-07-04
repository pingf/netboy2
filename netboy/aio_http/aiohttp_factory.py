import json
import re
import time

from netboy.base.base_factory import BaseFactory

from netboy.netboy import NetBoy
from netboy.util.loader import load





        # ['ATTRS', '__aenter__', '__aexit__', '__class__', '__del__', '__delattr__', '__dict__', '__dir__', '__doc__',
        #  '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__',
        #  '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__',
        #  '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_auto_decompress', '_body',
        #  '_cache', '_cleanup_writer', '_closed', '_connection', '_content_dict', '_content_type', '_continue',
        #  '_headers', '_history', '_loop', '_notify_content', '_parse_content_type', '_protocol', '_reader', '_real_url',
        #  '_request_info', '_response_eof', '_session', '_source_traceback', '_stored_content_type', '_timer', '_traces',
        #  '_url', '_writer', 'charset', 'close', 'closed', 'connection', 'content', 'content_disposition',
        #  'content_length', 'content_type', 'cookies', 'get_encoding', 'headers', 'history', 'host', 'json', 'links',
        #  'method', 'raise_for_status', 'raw_headers', 'read', 'real_url', 'reason', 'release', 'request_info', 'start',
        #  'status', 'text', 'url', 'url_obj', 'version', 'wait_for_close']

        # print(data)
        # print(dir(response))




class AIOHttpFactory(BaseFactory):

    # def __init__(self, data, info):
    #     super(AIOHttpFactory, self).__init__(data, info)


    async def run(self):
        ses = self.info.get('session')
        return await self.run_core_async('aiohttp', self.fetch, ses)


    async def fetch(self, data, session, json_response=False):
        if isinstance(data, str):
            data ={
                'url': data,
            }
        url = data.get('url')
        filter = data.get('filter')
        if not filter:
            filter = ['data', 'title', 'code']

        results = {'url': url}
        async with session.get(url) as response:
            # delay = response.headers.get("DELAY")
            # date = response.headers.get("DATE")
            # print("{}:{} with delay {}".format(date, response.url, delay))
            # content = await response.read()
            stream = data.get('stream')
            if isinstance(stream, dict):
                stream_func = stream.get('func')
                stream_func = load(stream_func)
                stream_chunk = stream.get('chunk', 512)
                stream_file = stream.get('file')
                count = 0
                if stream_file:
                    with open(stream_file, 'wb') as fd:
                        while True:
                            chunk = await response.content.read(stream_chunk)
                            count += 1
                            if not chunk:
                                break
                            stream_func(chunk, data, fd)
                else:
                    while True:
                        chunk = await resp.content.read(stream_chunk)
                        count += 1
                        if not chunk:
                            break
                        stream_func(chunk, data)
                results['stream'] = {
                    'chunk': stream_chunk,
                    'count': count
                }
            elif 'data' in filter or 'charset' in filter or 'title' in filter:
                charset = data.get('charset')
                if json_response is False:
                    if charset:
                        raw = await response.read()
                        content = raw.decode('utf8', errors='ignore')
                    else:
                        content = await response.text()
                else:
                    content = await response.json()

                match = re.search('<title[^>]*>([^<]+)</title>', content, re.IGNORECASE)
                title = match.group(1) if match else ''

                if 'data' in filter:
                    results['data'] = content
                if 'charset' in filter:
                    results['charset'] = charset
                if 'title' in filter:
                    results['title'] = title
            if 'headers' in filter:
                results['headers'] = {k:v for k,v in response.headers.items()}
            if 'cookies' in filter:
                results['cookies'] = {k:v for k,v in response.cookies.items()}
            if 'effect' in filter:
                results['effect'] = response.real_url
            if 'code' in filter:
                results['code'] = response.status
            if 'method' in filter:
                results['method'] = response.method
            return results

if __name__ == '__main__':
    info={'chunk_size': 1}
    data=['http://www.baidu.com', 'http://www.bing.com']#, 'http://www.google.com' ]
    # f = AIOHttpFactory(data, info)
    # f.run()
    boy = NetBoy(info=info)
    boy.use_mode('coroutine').use_spider('aiohttp').use_filter(['title', 'url', 'title', 'code', 'time'])
    resp = boy.run(data)
    # print(resp.keys())
    print(json.dumps(resp, indent=2, ensure_ascii=False))







