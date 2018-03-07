import json
import re

import pycurl
from bs4 import UnicodeDammit


def safe_cn_charset(charset):
    CHARSET_LIST = ["utf8", "gb2312", "gbk", "big5", "gb18030"]
    charset = charset.lower()
    charset = charset.replace('-', '')
    charset = charset.replace('_', '')
    if charset.endswith('18030'):
        return 'gb18030'
    if charset.endswith('2312'):
        return 'gb2312'
    if charset in CHARSET_LIST:
        return charset
    return 'utf8'


def beautify(data):
    charsets = ["utf8", "gb2312", "gbk", "big5", "gb18030"]
    dammit = UnicodeDammit(data, charsets, smart_quotes_to="html")
    charset = dammit.original_encoding
    data = dammit.unicode_markup
    # if charset in CHARSET_LIST:
    #     data = dammit.unicode_markup
    # else:
    #     charset = 'utf8'
    #     data = data.decode('utf8', 'ignore')

    return data, charset


def filter_content_result(c, json_response=False):
    result = {}
    curl_filter = c.data.get('filter')
    if not curl_filter:
        curl_filter=['data', 'charset', 'title']
    if 'data' in curl_filter or 'charset' in curl_filter or 'title' in curl_filter:
        body = c.databuf.getvalue()
        charset = None

        if c.charset:
            data = body.decode(c.charset, 'ignore')
        else:
            if len(body) == 0:
                data = ''
                charset = 'utf8'
            elif 'content-type' in c.headers:
                content_type = c.headers['content-type'].lower()
                match = re.search('charset=([a-zA-Z\-_0-9]+)', content_type)
                if match:
                    charset = match.group(1)
                charset = safe_cn_charset(charset)
                data = body.decode(charset, 'ignore')

            else:
                utf8_data = body.decode('utf8', 'ignore')
                match = re.search('charset=([a-zA-Z\-_0-9]+)', utf8_data)
                if match:
                    charset = match.group(1)
                    charset = safe_cn_charset(charset)
                    data = body.decode(charset, 'ignore')
                else:
                    data, charset = beautify(body)

        if c.data.get('json'):
            try:
                data = json.loads(data)
            except Exception as e:
                pass
            if 'data' in curl_filter:
                result['data'] = data
        else:
            if 'title' in curl_filter:

                match = re.search('<title[^>]*>([^<]+)</title>', data)
                if match:
                    result['title'] = match.group(1)
                else:
                    result['title'] = ''
            if 'data' in curl_filter:
                result['data'] = data
            if 'charset' in curl_filter:
                result['charset'] = charset
    return result



def filter_curl_result(c):
    filter_map = {
        'url': lambda curl: curl.data.get('url'),
        'effect': lambda curl: curl.getinfo(pycurl.EFFECTIVE_URL),
        'ip': lambda curl: curl.getinfo(pycurl.PRIMARY_IP),
        'port': lambda curl: curl.getinfo(pycurl.PRIMARY_PORT),
        'local_ip': lambda curl: curl.getinfo(pycurl.LOCAL_IP),
        'local_port': lambda curl: curl.getinfo(pycurl.LOCAL_PORT),
        'speed': lambda curl: curl.getinfo(pycurl.SPEED_DOWNLOAD),
        'size': lambda curl: curl.getinfo(pycurl.SIZE_DOWNLOAD),
        'redirect_count': lambda curl: curl.getinfo(pycurl.REDIRECT_COUNT),
        'redirect_url': lambda curl: curl.getinfo(pycurl.REDIRECT_URL),
        # 'http_code': lambda curl: curl.getinfo(pycurl.HTTP_CODE),
        'code': lambda curl: curl.getinfo(pycurl.RESPONSE_CODE),  # same as http_code
        'connect_code': lambda curl: curl.getinfo(pycurl.HTTP_CONNECTCODE),
        'content_type': lambda curl: curl.getinfo(pycurl.CONTENT_TYPE),

        'time': lambda curl: curl.getinfo(pycurl.TOTAL_TIME),
        # 'info_filetime': lambda curl: curl.getinfo(pycurl.INFO_FILETIME),
        'connect_time': lambda curl: curl.getinfo(pycurl.CONNECT_TIME),
        'namelookup_time': lambda curl: curl.getinfo(pycurl.NAMELOOKUP_TIME),
        'starttransfer_time': lambda curl: curl.getinfo(pycurl.STARTTRANSFER_TIME),
        'pretransfer_time': lambda curl: curl.getinfo(pycurl.PRETRANSFER_TIME),
        'redirect_time': lambda curl: curl.getinfo(pycurl.REDIRECT_TIME),
        'appconnect_time': lambda curl: curl.getinfo(pycurl.APPCONNECT_TIME),

        'header_size': lambda curl: curl.getinfo(pycurl.HEADER_SIZE),
        'request_size': lambda curl: curl.getinfo(pycurl.REQUEST_SIZE),
        'ssl_verifyresult': lambda curl: curl.getinfo(pycurl.SSL_VERIFYRESULT),
        'num_connects': lambda curl: curl.getinfo(pycurl.NUM_CONNECTS),
        'content_length_download': lambda curl: curl.getinfo(pycurl.CONTENT_LENGTH_DOWNLOAD),
        # 'cookielist': lambda curl: curl.getinfo(pycurl.INFO_COOKIELIST),
        'cookie': lambda curl: curl.getinfo(pycurl.INFO_COOKIELIST),

        'httpauth_avail': lambda curl: curl.getinfo(pycurl.HTTPAUTH_AVAIL),
        'proxyauth_avail': lambda curl: curl.getinfo(pycurl.PROXYAUTH_AVAIL),
        'os_errno': lambda curl: curl.getinfo(pycurl.OS_ERRNO),
        'ssl_engines': lambda curl: curl.getinfo(pycurl.SSL_ENGINES),
        'lastsocket': lambda curl: curl.getinfo(pycurl.LASTSOCKET),
        'ftp_entry_path': lambda curl: curl.getinfo(pycurl.FTP_ENTRY_PATH),
    }
    result = {}
    curl_filter = c.data.get('filter')
    if not curl_filter:
        curl_filter = ['url', 'effect', 'ip', 'port', 'time', 'code']
    for f in curl_filter:
        if f in filter_map.keys():
            result[f] = filter_map[f](c)
    return result


def get_result(c):
    result = {'state': 'normal', 'spider': 'pycurl'}
    curl_result = filter_curl_result(c)
    content_result = filter_content_result(c)
    result.update(curl_result)
    result.update(content_result)
    return result
