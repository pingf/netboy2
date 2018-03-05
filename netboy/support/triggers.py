from netboy.asyncio_pycurl.curl_one import work as curl_work


def trig_it(payload, response):
    print('*trigger*' * 20)
    print(payload)


def post_it(payload, response):
    trigger = payload.get('trigger')
    url = trigger.get('url')
    payload = {
        'url': url,
        'method': 'post',
        'postfields': {
            'payload': payload,
            'response': response
        }
    }
    resp = curl_work(payload, logger='netboy')
    # return resp
