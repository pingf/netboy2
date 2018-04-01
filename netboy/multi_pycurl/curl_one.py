import logging
import pycurl

from netboy.multi_pycurl.curl_result import get_result
from netboy.multi_pycurl.curl_setup import setup_curl


def work(data, logger='worker'):
    log = logging.getLogger(logger)
    curl = pycurl.Curl()
    curl.data = data
    setup_curl(curl)

    try:
        curl.perform()
        response = get_result(curl)
    except pycurl.error as e:
        err0 = e.args[0]
        err1 = e.args[1]
        log.warning('error: ' + str(err0) + ' ' + str(err1))
        response = get_result(curl)
        return response
    except Exception:
        log.exception('pycurl failed')
        return
    finally:
        curl.close()
    return response
