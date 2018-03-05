import json
import logging
from copy import copy

import pycurl

from asyncio import sleep

from netboy.asyncio_pycurl.curl_one import work as curl_work
from netboy.asyncio_pycurl.curl_result import get_result
from netboy.asyncio_pycurl.curl_setup import setup_curl
from netboy.celery.app import App


# from netboy.celery.tasks import trigger_task
from netboy.util.data_info import update_data_from_info


class CurlFactory:
    def __init__(self, data, info):
        self.log = logging.getLogger(info.get('log', 'netboy'))
        self.m = pycurl.CurlMulti()
        self.m.handles = []
        self.data = data
        self.info = info
        updated = update_data_from_info(data, info)
        self.queue = []
        for e in updated:
            url = e['url'].strip()
            e['url'] = url
            if not url or url[0] == "#":
                continue
            self.queue.append(e)

        self.num_urls = len(self.queue)
        self.num_conn = min(info.get('num_conn', 20), self.num_urls)

    def allocate(self):
        for i in range(self.num_conn):
            c = self.allocate1()
            self.m.handles.append(c)

    def allocate1(self):
        c = pycurl.Curl()
        return c

    def freelist(self):
        return self.m.handles[:]

    async def run(self):
        responses = []

        frees = self.freelist()

        num_processed = 0
        while num_processed < self.num_urls:
            # If there is an url to process and a free curl object, add to multi stack
            while self.queue and frees:
                data = self.queue.pop(0)
                url = data['url']
                c = frees.pop()
                setup_curl(c, data)
                self.m.add_handle(c)
                c.data = data

            # Run the internal curl state machine for the multi stack
            while 1:
                ret, num_handles = self.m.perform()
                if ret != pycurl.E_CALL_MULTI_PERFORM:
                    break
            # Check for curl objects which have terminated, and add them to the freelist
            while 1:
                num_q, ok_list, err_list = self.m.info_read()
                for c in ok_list:
                    self.m.remove_handle(c)
                    msg = "success! url: " + str(c.data.get('url')) + ' effect: ' + str(
                        c.getinfo(pycurl.EFFECTIVE_URL)) + ' code: ' + str(
                        c.getinfo(pycurl.HTTP_CODE))
                    self.log.info(msg)
                    res = get_result(c)

                    self.trigger_it(c.data, res)

                    frees.append(c)
                    res.pop('data', None)
                    responses.append(res)

                for c, errno, errmsg in err_list:
                    if errno in [28]:
                        msg = "28! url: " + str(c.data.get('url')) + ' errno: ' + str(errno) + ' errmsg: ' + str(
                            errmsg)
                        self.log.warning(msg)
                        res = get_result(c)
                        res['errno'] = errno
                        res['errmsg'] = errmsg
                        self.trigger_it(c.data, res)
                        res.pop('data', None)
                        responses.append(res)
                    else:
                        msg = "failed! url: " + str(c.data.get('url')) + ' errno: ' + str(errno) + ' errmsg: ' + str(
                            errmsg)
                        self.log.warning(msg)

                        if c.data.get('retry'):
                            await sleep(0.2)
                            response = curl_work(c.data, c.data.get('log', 'netboy'))
                            if response:
                                await sleep(0.1)
                                res = get_result(c)
                                self.trigger_it(c.data, res)
                                res.pop('data', None)
                                responses.append(res)
                            else:
                                res = {
                                    'state': 'error',
                                    'spider': 'pycurl',
                                    'errno': errno,
                                    'errmsg': errmsg
                                }
                                responses.append(res)
                        else:
                            res = {
                                'state': 'error',
                                'spider': 'pycurl',
                                'errno': errno,
                                'errmsg': errmsg
                            }
                            responses.append(res)
                    self.trigger_it(c.data, res)
                    self.m.remove_handle(c)
                    frees.append(c)
                num_processed = num_processed + len(ok_list) + len(err_list)
                if num_q == 0:
                    break
            # Currently no more I/O is pending, could do something in the meantime
            # (display a progress bar, etc.).
            # We just call select() to sleep until some more data is available.
            self.m.select(0.2)
            await sleep(0.1)
        self.anaylse_it(responses)
        return responses

    def anaylse_it(self, responses):
        payload = self.info
        payload.pop('dummy', None)
        payload.pop('session', None)
        payload.pop('semaphore', None)
        analysers = payload.get('analysers')
        if analysers:
            for analyser in analysers:
                payload['analyser'] = analyser
                sig = {
                    #here the payload is the info
                    'payload': payload,
                    'response': responses,
                }
                try:
                   App().app.send_task('netboy.celery.tasks.analyser_task', kwargs=sig, countdown=1,
                                  queue=self.info.get('queue', 'worker'),
                                  routing_key=self.info.get('queue', 'worker'))
                except Exception as e:
                    self.log.critical('analyser failed: '+str(e))

    def trigger_it(self, payload, response):
        triggers = payload.pop('triggers', None)
        payload.pop('dummy', None)
        payload.pop('session', None)
        payload.pop('semaphore', None)
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
                    self.log.critical('trigger failed: '+str(e))
