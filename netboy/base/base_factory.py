import logging
import time

from netboy.util.data_info import update_data_from_info
from netboy.util.loader import load

from netboy.celery.app import App


class BaseFactory:
    def __init__(self, data, info):
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

            if isinstance(response, dict):
                if response.get('update'):
                    response['update'] = False
        return response

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

    async def run_core_async(self, spider, func, extra=None):
        func = load(func) if isinstance(func, str) else func
        responses = []
        print(self.updated, '.....')
        for d in self.updated:
            prepare_resp = self.prepare_it(d)
            url = d.get('url') if isinstance(d, dict) else d

            if isinstance(prepare_resp, dict):
                if prepare_resp.get('skip'):
                    continue
                if prepare_resp.get('cover'):
                    response = self.trigger_it(d, prepare_resp)
                    responses.append(response)
                    continue
            start = time.time()
            try:
                response = await func(d, extra)
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
                        'spider': spider,
                        'state': 'error',
                        "code": -2,
                        "time": response_time
                    }
                else:
                    end = time.time()
                    d['time'] = '%s' % (end - start)
                    msg = "success! url: " + str(url)
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
                    'spider': spider,
                    'state': 'error',
                    "code": -1,
                    "time": response_time
                }
            response = self.trigger_it(d, response)
            responses.append(response)
        self.anaylse_it(responses)
        return responses

    def run_core(self, spider, func, extra=None):
        func = load(func) if isinstance(func, str) else func
        responses = []
        for d in self.updated:
            prepare_resp = self.prepare_it(d)
            url = d.get('url') if isinstance(d, dict) else d

            if isinstance(prepare_resp, dict):
                if prepare_resp.get('skip'):
                    continue
                if prepare_resp.get('cover'):
                    response = self.trigger_it(d, prepare_resp)
                    responses.append(response)
                    continue
            start = time.time()
            try:
                response = func(d, extra)
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
                        'spider': spider,
                        'state': 'error',
                        "code": -2,
                        "time": response_time
                    }
                else:
                    end = time.time()
                    d['time'] = '%s' % (end - start)
                    msg = "success! url: " + str(url)
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
                    'spider': spider,
                    'state': 'error',
                    "code": -1,
                    "time": response_time
                }
            response = self.trigger_it(d, response)
            responses.append(response)
        self.anaylse_it(responses)
        return responses
