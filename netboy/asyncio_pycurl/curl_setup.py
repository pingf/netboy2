import json
from io import BytesIO

import re

import pycurl
from netboy.util.loader import load

DEFAULT_USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64; compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm; Baiduspider/2.0; +http://www.baidu.com/search/spider.html) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80() Safari/537.36'


def setup_curl(c, d):
    databuf = BytesIO()
    headers = {'count': 0, 'content': [{}]}
    set_cookies = []

    c.databuf = databuf
    c.headers = headers
    if d.get('charset'):
        c.charset = d.get('charset')
    else:
        c.charset = None

    if d.get('cn'):
        c.cn = True
    else:
        c.cn = None

    def header_function(header_line):
        match = re.match("^Set-Cookie: (.*)$", header_line.decode('utf8', 'ignore'))
        if match:
            set_cookies.append(match.group(1))
        count = headers['count']
        header_line = header_line.decode('iso-8859-1')
        if ':' not in header_line and not header_line.startswith('HTTP'):
            # print(header_line)
            if '\r\n' in header_line:
                headers['count'] += 1
                headers['content'].append({})
            return
        # Break the header line into header name and value.
        if ':' in header_line:
            name, value = header_line.rstrip('\r\n').split(':', 1)
        else:
            name, value = header_line.rstrip('\r\n').split(' ', 1)

        # Remove whitespace that may be present.
        # Header lines include the trailing newline, and there may be whitespace
        # around the colon.
        name = name.strip()
        value = value.strip()

        # Header names are case insensitive.
        # Lowercase name here.
        name = name.lower()

        # Now we can actually record the header name and value.
        if name in headers['content'][count]:
            headers['content'][count][name].append(value)
        else:
            headers['content'][count][name] = [value]

    def write_function(buf):
        size = databuf.getbuffer().nbytes
        if size < 4096000:
            databuf.write(buf)
            return len(buf)
        return 0

    c.setopt(pycurl.FOLLOWLOCATION, d.get('followlocation', 1))
    c.setopt(pycurl.MAXREDIRS, d.get('followlocation', 1))
    c.setopt(pycurl.CONNECTTIMEOUT, d.get('connecttimeout', 30))
    c.setopt(pycurl.TIMEOUT, d.get('timeout', 300))
    c.setopt(pycurl.NOSIGNAL, d.get('nosignal', 1))
    c.setopt(pycurl.USERAGENT, d.get('useragent', DEFAULT_USER_AGENT))
    c.setopt(pycurl.SSL_VERIFYPEER, d.get('ssl_verifypeer', 0))
    c.setopt(pycurl.SSL_VERIFYHOST, d.get('ssl_verifyhost', 0))

    crawl_url = d.get('effect') or d.get('url')
    if not crawl_url.startswith('http'):
        crawl_url = 'http://' + crawl_url
    c.setopt(pycurl.URL, crawl_url.encode('utf-8'))
    # c.setopt(pycurl.URL, url)

    headerfunction = d.get('headerfunction')
    if headerfunction is None:
        c.setopt(pycurl.HEADERFUNCTION, header_function)
    else:
        c.setopt(pycurl.HEADERFUNCTION, load(headerfunction))
    writefunction = d.get('writefunction')
    if writefunction is None:
        c.setopt(pycurl.WRITEFUNCTION, write_function)
    else:
        c.setopt(pycurl.WRITEFUNCTION, load(writefunction))

    method = d.get('method', 'get')

    if method == 'get':
        httpheader = d.get('httpheader')
        if httpheader:
            c.setopt(c.HTTPHEADER, httpheader)
    elif method == 'post':
        httpheader = d.get('httpheader', ['Accept: application/json', "Content-type: application/json"])
        if httpheader:
            # curl.setopt(pycurl.HEADER, p.get('header', 1))
            c.setopt(pycurl.HTTPHEADER, httpheader)
        post301 = getattr(pycurl, 'POST301', None)
        if post301 is not None:
            # Added in libcurl 7.17.1.
            c.setopt(post301, True)
        c.setopt(pycurl.POST, 1)
        postfields = d.get('postfields')
        if postfields:
            postfields = json.dumps(postfields)
            c.setopt(pycurl.POSTFIELDS, postfields)
    elif method == 'postform':
        httpheader = d.get('httpheader', ["Content-Type: application/x-www-form-urlencoded"])
        if httpheader:
            c.setopt(pycurl.HTTPHEADER, httpheader)
        post301 = getattr(pycurl, 'POST301', None)
        if post301 is not None:
            # Added in libcurl 7.17.1.
            c.setopt(post301, True)
        c.setopt(pycurl.POST, 1)
        httppost = d.get('postform')
        if httppost:
            c.setopt(pycurl.POSTFIELDS, httppost)
    proxy_type = d.get('proxytype')
    proxy = d.get('proxy')
    proxy_port = d.get('proxyport')
    proxy_userpwd = d.get('proxyuserpwd')
    if proxy:
        c.setopt(pycurl.PROXY, proxy)
    if proxy_port:
        c.setopt(pycurl.PROXYPORT, proxy_port)
    if proxy_userpwd:
        c.setopt(pycurl.PROXYUSERPWD, proxy_userpwd)
    if proxy_type:
        if '4' in proxy_type:
            proxy_type = pycurl.PROXYTYPE_SOCKS4A
        elif '5' in proxy_type:
            proxy_type = pycurl.PROXYTYPE_SOCKS5_HOSTNAME
        else:
            proxy_type = pycurl.PROXYTYPE_HTTP
        c.setopt(pycurl.PROXYTYPE, proxy_type)

    verbose = d.get('verbose')
    if verbose:
        c.setopt(pycurl.VERBOSE, True)
    # with the line below, redirect cookie can update
    c.setopt(pycurl.COOKIEFILE, "")

    cookie = d.get('cookie')
    if cookie:
        c.setopt(pycurl.COOKIE, cookie)
    c.setopt(pycurl.FAILONERROR, True)

    http_version = d.get('http_version')
    if http_version == '1.1' or http_version == 1.1:
        c.setopt(pycurl.HTTP_VERSION, pycurl.CURL_HTTP_VERSION_1_1)
    else:
        c.setopt(pycurl.HTTP_VERSION, pycurl.CURL_HTTP_VERSION_1_0)
