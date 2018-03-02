import logging
import pycurl

from netboy.asyncio_pycurl.curl_setup import setup_curl


def work(data, logger='worker'):
    log = logging.getLogger(logger)
    curl = pycurl.Curl()
    setup_curl(curl, data)
    try:
        response = curl.perform()
    except pycurl.error as e:
        err0 = e.args[0]
        err1 = e.args[1]
        log.warning('error: ' + str(err0) + ' ' + str(err1))
        return
    except Exception:
        log.exception('pycurl failed')
        return
    finally:
        curl.close()
    return response
