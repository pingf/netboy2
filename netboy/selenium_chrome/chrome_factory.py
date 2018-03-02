import base64
import logging

import time

import selenium
from selenium import webdriver

from netboy.celery.app import App
from netboy.selenium_chrome.chrome_result import get_result
from netboy.util.data_info import update_data_from_info
from netboy.util.loader import load


class ChromeFactory:
    def __init__(self, data, info):
        self.log = logging.getLogger(info.get('logger_name', 'worker'))
        self.data = data
        self.info = info
        updated = update_data_from_info(data, info)

        for e in updated:
            url = e['url'].strip()
            e['url'] = url
            if not url or url[0] == "#":
                continue
        self.updated = updated
        self.driver = None

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

            options.add_argument('window-size=' + window_size)
            # options.add_argument('--proxy-server=http://127.0.0.1:8123')
            # options.add_argument('--proxy-server=https://127.0.0.1:8123')
            # options.add_argument('--proxy-server=socks5://127.0.0.1:1082')
            if proxy and proxy_type and proxy_port:
                options.add_argument('--proxy-server=%s://%s:%d' % (proxy_type, proxy, proxy_port))

            self.driver = webdriver.Chrome(chrome_options=options)
        responses = []
        try:
            for d in self.updated:
                load_timeout = d.get('timeout', 15)
                implicit_wait = d.get('wait', 5)

                start = time.time()
                try:
                    url = d.get('url')
                    self.driver.set_page_load_timeout(load_timeout)
                    self.driver.get(url)
                    self.driver.implicitly_wait(implicit_wait)
                    interact = d.get('interactive')
                    if interact:
                        inter_func = load(interact)
                        inter_func(d, self.driver)
                    end = time.time()
                    d['time'] = '%s' % (end - start)
                    response = get_result(d, self.driver)
                # except selenium.common.exceptions.TimeoutException as e:
                #     end = time.time()
                #     self.log.critical('crawl timeout: ' + str(e)+' '+str(type(e)))
                #     d['time'] = '%s' % (end - start)
                #     print(self.driver.get_network_conditions(), '~*'*40)
                #
                #     response = get_result(d, self.driver)
                except Exception as e:
                    end = time.time()
                    response_time = '%s' % (end - start)
                    self.log.critical('crawl failed for %s: '%url + str(e)+' '+str(type(e)))
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
                responses.append(response)
                self.trigger_it(d, response)
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
                    App().app.send_task('netboy.celery.tasks.analyser_task', kwargs=sig, countdown=1,
                                  queue=self.info.get('queue', 'worker'),
                                  routing_key=self.info.get('queue', 'worker'))
                except Exception as e:
                    self.log.critical('analyser failed: ' + str(e))

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
                payload['trigger'] = trigger
                sig = {
                    'payload': payload,
                    'response': response,
                }
                try:
                    App().app.send_task('netboy.celery.tasks.trigger_task', kwargs=sig, countdown=1,
                                  queue=payload.get('queue'),
                                  routing_key=payload.get('queue'))
                except Exception as e:
                    self.log.critical('trigger failed: ' + str(e))


if __name__ == '__main__':
    info = {
        'screenshot': True
    }
    data = ['http://www.douban.com']
    f = ChromeFactory(data, info)
    r = f.run()
    print(r)
