import logging

from asyncio import sleep
import time

from selenium import webdriver

from netboy.celery.app import App
from netboy.selenium_chrome.chrome_result import get_result
from netboy.util.data_info import update_data_from_info
from netboy.util.loader import load
from netboy.util.timeout import timeout, exit_after


# @exit_after(15)
def crawl(driver, data):
    url = data.get('url')
    crawl_url = data.get('effect') or url
    if not crawl_url.startswith('http'):
        crawl_url = 'http://' + crawl_url
    driver.get(crawl_url)
    response = get_result(data, driver)
    return response


class ChromeFactory:
    def __init__(self, data, info):
        self.log = logging.getLogger(info.get('logger_name', 'worker'))
        self.data = data
        self.info = info
        self.log = logging.getLogger(info.get('log', 'netboy'))
        updated = update_data_from_info(data, info)

        for e in updated:
            url = e['url'].strip()
            e['url'] = url
            if not url or url[0] == "#":
                continue
        self.updated = updated
        self.driver = None

    async def async_run(self):
        if not self.driver:
            chrome_bin = self.info.get('chrome', '/opt/google/chrome-beta/chrome')
            window_size = self.info.get('window_size', '1920x1080')
            proxy_type = self.info.get('proxytype')
            user_agent = self.info.get('useragent')
            if proxy_type == '5':
                proxy_type = 'socks5'
            if proxy_type == '4':
                proxy_type = 'socks4'
            proxy = self.info.get('proxy')
            proxy_port = self.info.get('proxyport')

            options = webdriver.ChromeOptions()
            options.binary_location = chrome_bin
            options.add_argument("user-agent=%s" % user_agent)
            # options.add_argument('headless')
            options.set_headless(headless=True)

            options.add_argument('window-size=' + window_size)
            options.add_argument('--no-referrers')
            # options.add_argument('--proxy-server=http://127.0.0.1:8123')
            # options.add_argument('--proxy-server=https://127.0.0.1:8123')
            # options.add_argument('--proxy-server=socks5://127.0.0.1:1082')
            if proxy and proxy_type and proxy_port:
                options.add_argument('--proxy-server=%s://%s:%d' % (proxy_type, proxy, proxy_port))

            self.driver = webdriver.Chrome(chrome_options=options)
            load_timeout = self.info.get('timeout', 15)
            script_timeout = self.info.get('script_timeout', 15)
            implicit_wait = self.info.get('wait', 5)
            self.driver.implicitly_wait(implicit_wait)
            self.driver.set_page_load_timeout(load_timeout)
            self.driver.set_script_timeout(script_timeout)
        responses = []

        try:
            crawl_func = exit_after(load_timeout)(crawl)
            for d in self.updated:

                ret_data = self.prepare_it(d)

                if isinstance(ret_data, dict):
                    d = ret_data
                    if d.get('skip'):
                        continue

                start = time.time()
                url = d.get('url')
                try:
                    response = crawl_func(self.driver, d)
                    if response is None:
                        end = time.time()
                        response_time = '%s' % (end - start)
                        msg = "failed! url: " + str(url)
                        self.log.warning(msg)
                        response = {
                            'url': url,
                            'effect': url,
                            'data': '',
                            'title': '',
                            'spider': 'chrome',
                            'state': 'error',
                            "code": -2,
                            "time": response_time
                        }
                    else:
                        interact = d.get('interactive')
                        if interact:
                            inter_func = load(interact)
                            inter_func(d, self.driver)
                        end = time.time()
                        d['time'] = '%s' % (end - start)
                        msg = "success! url: " + str(url) + ' effect: ' + str(self.driver.current_url)
                        self.log.info(msg)
                except Exception as e:
                    end = time.time()
                    response_time = '%s' % (end - start)
                    msg = "failed! url: " + str(url) + ' errtype: ' + str(type(e)) + ' errmsg: ' + str(e)
                    self.log.warning(msg)
                    response = {
                        'url': url,
                        'effect': url,
                        'data': '',
                        'title': '',
                        'spider': 'chrome',
                        'state': 'error',
                        "code": -1,
                        "time": response_time
                    }
                response = self.trigger_it(d, response)
                response.pop('data', None)
                response.pop('screen', None)
                responses.append(response)
            self.anaylse_it(responses)
        finally:
            self.driver.quit()
            self.driver = None
        return responses

    def run(self):
        if not self.driver:
            chrome_bin = self.info.get('chrome', '/opt/google/chrome-beta/chrome')
            window_size = self.info.get('window_size', '1920x1080')
            proxy_type = self.info.get('proxytype')
            if proxy_type == '5':
                proxy_type = 'socks5'
            if proxy_type == '4':
                proxy_type = 'socks4'
            proxy = self.info.get('proxy')
            proxy_port = self.info.get('proxyport')

            options = webdriver.ChromeOptions()
            options.binary_location = chrome_bin
            # options.add_argument('headless')
            options.set_headless(headless=True)
            options.add_argument("--dns-prefetch-disable")
            options.add_argument('--no-referrers')

            options.add_argument('window-size=' + window_size)
            # options.add_argument('--proxy-server=http://127.0.0.1:8123')
            # options.add_argument('--proxy-server=https://127.0.0.1:8123')
            # options.add_argument('--proxy-server=socks5://127.0.0.1:1082')
            if proxy and proxy_type and proxy_port:
                options.add_argument('--proxy-server=%s://%s:%d' % (proxy_type, proxy, proxy_port))

            self.driver = webdriver.Chrome(chrome_options=options)
            load_timeout = self.info.get('timeout', 15)
            script_timeout = self.info.get('script_timeout', 15)
            implicit_wait = self.info.get('wait', 5)
            self.driver.implicitly_wait(implicit_wait)
            self.driver.set_page_load_timeout(load_timeout)
            self.driver.set_script_timeout(script_timeout)

        responses = []
        try:
            crawl_func = exit_after(load_timeout)(crawl)
            for d in self.updated:

                ret_data = self.prepare_it(d)

                if isinstance(ret_data, dict):
                    d = ret_data
                    if d.get('skip'):
                        continue
                start = time.time()
                url = d.get('url')
                try:
                    response = crawl_func(self.driver, d)
                    if response is None:
                        end = time.time()
                        response_time = '%s' % (end - start)
                        msg = "failed! url: " + str(url)
                        self.log.warning(msg)
                        response = {
                            'url': url,
                            'effect': url,
                            'data': '',
                            'title': '',
                            'spider': 'chrome',
                            'state': 'error',
                            "code": -2,
                            "time": response_time
                        }
                    else:
                        interact = d.get('interactive')
                        if interact:
                            inter_func = load(interact)
                            inter_func(d, self.driver)
                        end = time.time()
                        d['time'] = '%s' % (end - start)
                        msg = "success! url: " + str(url) + ' effect: ' + str(self.driver.current_url)
                        self.log.info(msg)

                except Exception as e:
                    end = time.time()
                    response_time = '%s' % (end - start)
                    msg = "failed! url: " + str(url) + ' errtype: ' + str(type(e)) + ' errmsg: ' + str(e)
                    self.log.warning(msg)
                    response = {
                        'url': url,
                        'effect': url,
                        'data': '',
                        'title': '',
                        'spider': 'chrome',
                        'state': 'error',
                        "code": -1,
                        "time": response_time
                    }
                response = self.trigger_it(d, response)
                response.pop('data', None)
                response.pop('screen', None)
                responses.append(response)
            self.anaylse_it(responses)
        finally:
            self.driver.quit()
            self.driver = None
        return responses

    def anaylse_it(self, responses):
        payload = self.info
        analysers = payload.get('analysers')
        if analysers:
            for analyser in analysers:
                payload['analyser'] = analyser
                sig = {
                    # here the payload is the info
                    'payload': payload,
                    'response': responses,
                }
                try:
                    if payload.get('mode', 'celery') == 'celery':
                        App().app.send_task('netboy.celery.tasks.analyser_task', kwargs=sig, countdown=1,
                                                   queue=self.info.get('queue', 'worker'),
                                                   routing_key=self.info.get('queue', 'worker'))
                    else:
                        analyser_func = load(analyser) if isinstance(analyser, str) else load(analyser.get('analyser'))
                        resp = analyser_func(responses)
                        if resp is not None:
                            responses = resp
                except Exception as e:
                    self.log.critical('analyser failed: ' + str(e))

        return responses

    def prepare_it(self, data):
        prepares = data.pop('prepares', None)
        if prepares:
            for prepare in prepares:
                data['prepare'] = prepare
                try:
                    prepare_func = load(prepare) if isinstance(prepare, str) else load(prepare.get('prepare'))
                    resp = prepare_func(data)
                    if resp is not None:
                        if resp.get('update'):
                            data = resp

                except Exception as e:
                    self.log.critical('prepare failed: ' + str(e) + ' type: ' + str(type(e)))
        return data

    def trigger_it(self, payload, response):
        triggers = payload.pop('triggers', None)
        if triggers:
            for trigger in triggers:
                # if url:
                # pay['job_id'] = payload.get('job_id')
                # pay['job_name'] = payload.get('job_name')
                # pay['task_id'] = payload.get('task_id')
                # pay['task_name'] = payload.get('task_name')
                # pay['url'] = payload.get('url')
                if isinstance(trigger, str):
                    trigger = {'trigger': trigger}
                payload['trigger'] = trigger
                sig = {
                    'payload': payload,
                    'response': response,
                }
                try:
                    if trigger.get('mode', 'sync') == 'celery' and payload.get('mode') == 'celery':
                        App().app.send_task('netboy.celery.tasks.trigger_task', kwargs=sig, countdown=1,
                                                   queue=payload.get('queue'),
                                                   routing_key=payload.get('queue'))
                    else:
                        trigger_func = load(trigger) if isinstance(trigger, str) else load(trigger.get('trigger'))
                        resp = trigger_func(payload, response)
                        if resp:
                            if resp.get('update'):
                                response = resp
                except Exception as e:
                    self.log.critical('trigger failed: ' + str(e))
        return response


if __name__ == '__main__':
    info = {
        # 'screen': True
    }
    data = ['http://www.douban.com']
    f = ChromeFactory(data, info)
    r = f.run()
    print(r)
