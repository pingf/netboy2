import logging

from worker.celery import celery_coroutine_worker, celery_thread_worker
from wrap.exception import safe
from wrap.show import show

from netboy.asyncio_pycurl.async_handler import curl_handler
from netboy.celery.app import App
from netboy.selenium_chrome.chrome_driver_handler import chrome_driver_handler

from netboy.util.loader import load

app = App().app

coroutine_worker = app.task(bind=True)(celery_coroutine_worker)
thread_worker = app.task(bind=True)(celery_thread_worker)


@show(name='netboy')
@safe(Exception, return_value={"state": "error"})
async def coroutine_worker_do_crawl(data, info):
    logger = info.get('log', 'netboy')
    log = logging.getLogger(logger)
    log.info('coroutine worker do crawl!')
    resp = await curl_handler(data, info)
    return resp


@show(name='netboy')
@safe(Exception, return_value={"state": "error"})
def thread_worker_do_crawl(data, info):
    logger = info.get('log', 'netboy')
    log = logging.getLogger(logger)
    log.info('thread worker do crawl!')
    resp = chrome_driver_handler(data, info)
    return resp


@safe(Exception, return_value={"state": "error"})
def test(data, info):
    print('data:' + str(data))
    print('info:' + str(info))
    return 'test'


@app.task
def dummy(*args, **kwargs):
    return "OK"


@app.task
def trigger_task(payload, response):
    result = {}
    trigger = payload.get('trigger')
    if isinstance(trigger, str):
        trigger_it = load(trigger)
        trigger_result = trigger_it(payload, response)
        result['trigger'] = trigger_result
    else:
        if 'trigger' in trigger:
            trigger_it = load(trigger.get('trigger'))
            trigger_result = trigger_it(payload, response)
            result['trigger'] = trigger_result
    response.pop('data', None)
    result['payload'] = payload
    result['response'] = response
    return result


@app.task
def analyser_task(payload, response):
    result = {}
    analyser = payload.get('analyser')
    if isinstance(analyser, str):
        analyse_it = load(analyser)
        analyse_result = analyse_it(payload, response)
        result['analyse'] = analyse_result
    else:
        if 'analyser' in analyser:
            analyse_it = load(analyser.get('analyser'))
            analyse_result = analyse_it(payload, response)
            result['analyser'] = analyse_result
    result['payload'] = payload
    result['response'] = response
    return result
