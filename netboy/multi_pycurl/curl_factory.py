import logging

from logcc.util.table import trace_table

from netboy.util.loader import load
import pycurl

# from asyncio import sleep

from netboy.multi_pycurl.curl_one import work as curl_work
from netboy.multi_pycurl.curl_result import get_result
from netboy.multi_pycurl.curl_setup import setup_curl
from netboy.celery.app import App

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
        self.num_processed = 0
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

    def run(self):
        responses = []

        frees = self.freelist()

        def setup_loop():
            while self.queue and frees:
                data = self.queue.pop(0)
                url = data['url']
                c = frees.pop()

                prepare_resp = self.prepare_it(data)

                if isinstance(prepare_resp, dict):
                    if prepare_resp.get('skip'):
                        self.num_urls -= 1
                        return data, prepare_resp
                    if prepare_resp.get('cover'):
                        self.num_processed += 1
                        return data, prepare_resp
                c.data = data
                setup_curl(c)
                self.m.add_handle(c)
            return None, None

        while self.num_processed < self.num_urls:
            p, r = setup_loop()
            if r and isinstance(r, dict):
                if r.get('skip'):
                    continue
                if r.get('cover'):
                    res = self.trigger_it(p, r)
                    if self.info.get('mode') == 'celery':
                        res.pop('data', None)
                    responses.append(res)
                    continue

            # res = self.trigger_it(, res)

            # Run the internal curl state machine for the multi stack
            while 1:
                ret, num_handles = self.m.perform()
                if ret != pycurl.E_CALL_MULTI_PERFORM:
                    break
            # Check for curl objects which have terminated, and add them to the freelist
            while 1:
                res = None
                num_q, ok_list, err_list = self.m.info_read()
                for c in ok_list:
                    self.m.remove_handle(c)
                    msg = "success! url: " + str(c.data.get('url')) + ' effect: ' + str(
                        c.getinfo(pycurl.EFFECTIVE_URL)) + ' code: ' + str(
                        c.getinfo(pycurl.HTTP_CODE))
                    self.log.info(msg)
                    res = get_result(c)
                    res = self.trigger_it(c.data, res)
                    if self.info.get('mode') == 'celery':
                        res.pop('data', None)
                    responses.append(res)
                    frees.append(c)

                for c, errno, errmsg in err_list:
                    if errno == 28 and errmsg.startswith('O'):
                        msg = "28! url: " + str(c.data.get('url')) + ' errno: ' + str(errno) + ' errmsg: ' + str(
                            errmsg)
                        self.log.warning(msg)
                        res = get_result(c)
                        res['state'] = 'error'
                        res['errno'] = errno
                        res['errmsg'] = errmsg
                        res['url'] = c.data.get('url')
                    else:
                        msg = "failed! url: " + str(c.data.get('url')) + ' errno: ' + str(errno) + ' errmsg: ' + str(
                            errmsg)
                        self.log.warning(msg)

                        if c.data.get('retry'):
                            response = curl_work(c.data, c.data.get('log', 'netboy'))
                            if response:
                                res = get_result(c)
                            else:
                                res = {
                                    'url': c.data.get('url'),
                                    'state': 'error',
                                    'spider': 'pycurl',
                                    'errno': errno,
                                    'errmsg': errmsg
                                }
                        else:
                            res = {
                                'url': c.data.get('url'),
                                'state': 'error',
                                'spider': 'pycurl',
                                'errno': errno,
                                'errmsg': errmsg
                            }
                    res = self.trigger_it(c.data, res)
                    if self.info.get('mode') == 'celery':
                        res.pop('data', None)
                    responses.append(res)
                    self.m.remove_handle(c)
                    frees.append(c)
                self.num_processed = self.num_processed + len(ok_list) + len(err_list)
                if num_q == 0:
                    break
            # Currently no more I/O is pending, could do something in the meantime
            # (display a progress bar, etc.).
            # We just call select() to sleep until some more data is available.
            self.m.select(0.1)
        self.anaylse_it(responses)
        return responses

    # async def run(self):
    #     responses = []
    #
    #     frees = self.freelist()
    #
    #     def setup_loop():
    #         while self.queue and frees:
    #             data = self.queue.pop(0)
    #             url = data['url']
    #             c = frees.pop()
    #
    #             prepare_resp = self.prepare_it(data)
    #
    #             if isinstance(prepare_resp, dict):
    #                 if prepare_resp.get('skip'):
    #                     self.num_urls -= 1
    #                     return data, prepare_resp
    #                 if prepare_resp.get('cover'):
    #                     self.num_processed += 1
    #                     return data, prepare_resp
    #             c.data = data
    #             setup_curl(c)
    #             self.m.add_handle(c)
    #         return None, None
    #
    #     while self.num_processed < self.num_urls:
    #         p, r = setup_loop()
    #         if r and isinstance(r, dict):
    #             if r.get('skip'):
    #                 continue
    #             if r.get('cover'):
    #                 res = self.trigger_it(p, r)
    #                 if self.info.get('mode') == 'celery':
    #                     res.pop('data', None)
    #                 responses.append(res)
    #                 continue
    #
    #         # Run the internal curl state machine for the multi stack
    #         while 1:
    #             ret, num_handles = self.m.perform()
    #             if ret != pycurl.E_CALL_MULTI_PERFORM:
    #                 break
    #         # Check for curl objects which have terminated, and add them to the freelist
    #         while 1:
    #             res = None
    #             num_q, ok_list, err_list = self.m.info_read()
    #             for c in ok_list:
    #                 self.m.remove_handle(c)
    #                 msg = "success! url: " + str(c.data.get('url')) + ' effect: ' + str(
    #                     c.getinfo(pycurl.EFFECTIVE_URL)) + ' code: ' + str(
    #                     c.getinfo(pycurl.HTTP_CODE))
    #                 self.log.info(msg)
    #                 res = get_result(c)
    #
    #                 res = self.trigger_it(c.data, res)
    #                 if self.info.get('mode') == 'celery':
    #                     res.pop('data', None)
    #                 responses.append(res)
    #                 frees.append(c)
    #
    #             for c, errno, errmsg in err_list:
    #                 if errno in [28]:
    #                     msg = "28! url: " + str(c.data.get('url')) + ' errno: ' + str(errno) + ' errmsg: ' + str(
    #                         errmsg)
    #                     self.log.warning(msg)
    #                     res = get_result(c)
    #                     res['state'] = 'error'
    #                     res['errno'] = errno
    #                     res['errmsg'] = errmsg
    #                     res['url'] = c.data.get('url')
    #                 else:
    #                     msg = "failed! url: " + str(c.data.get('url')) + ' errno: ' + str(errno) + ' errmsg: ' + str(
    #                         errmsg)
    #                     self.log.warning(msg)
    #
    #                     if c.data.get('retry'):
    #                         await sleep(0.2)
    #                         response = curl_work(c.data, c.data.get('log', 'netboy'))
    #                         if response:
    #                             await sleep(0.1)
    #                             res = get_result(c)
    #                         else:
    #                             res = {
    #                                 'url': c.data.get('url'),
    #                                 'state': 'error',
    #                                 'spider': 'pycurl',
    #                                 'errno': errno,
    #                                 'errmsg': errmsg
    #                             }
    #                     else:
    #                         res = {
    #                             'url': c.data.get('url'),
    #                             'state': 'error',
    #                             'spider': 'pycurl',
    #                             'errno': errno,
    #                             'errmsg': errmsg
    #                         }
    #
    #                 res = self.trigger_it(c.data, res)
    #                 if self.info.get('mode') == 'celery':
    #                     res.pop('data', None)
    #                 responses.append(res)
    #                 self.m.remove_handle(c)
    #                 frees.append(c)
    #             self.num_processed = self.num_processed + len(ok_list) + len(err_list)
    #             if num_q == 0:
    #                 break
    #         # Currently no more I/O is pending, could do something in the meantime
    #         # (display a progress bar, etc.).
    #         # We just call select() to sleep until some more data is available.
    #         self.m.select(0.2)
    #         # await sleep(0.1)
    #     self.anaylse_it(responses)
    #     return responses

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
                    self.log.critical('analyser failed: ' + str(e) + ' type: ' + str(type(e)))
        return responses

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
                if isinstance(trigger, str):
                    trigger = {'trigger': trigger}
                payload['trigger'] = trigger
                sig = {
                    'payload': payload,
                    'response': response,
                }
                try:
                    if trigger.get('mode', 'sync') == 'celery' and payload.get('mode') == 'celery':
                        resp = App().app.send_task('netboy.celery.tasks.trigger_task', kwargs=sig, countdown=1,
                                                   queue=payload.get('queue'),
                                                   routing_key=payload.get('queue'))
                    else:
                        trigger_func = load(trigger) if isinstance(trigger, str) else load(trigger.get('trigger'))
                        resp = trigger_func(payload, response)
                        if resp:
                            if resp.get('update'):
                                response = resp

                except Exception as e:
                    trace_table(e)
                    self.log.critical('trigger failed: ' + str(e) + ' type: ' + str(type(e)))

            if isinstance(response, dict):
                if response.get('update'):
                    response['update'] = False
        return response

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
            if isinstance(data, dict):
                if data.get('update'):
                    data['update'] = False
        return data
