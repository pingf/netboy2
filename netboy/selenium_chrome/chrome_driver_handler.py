import logging

from netboy.selenium_chrome.chrome_factory import ChromeFactory


def chrome_driver_handler(data, info):
    factory = ChromeFactory(data, info)
    r = factory.run()
    return r


# def async_chrome_driver_handler(data, info):
#     factory = ChromeFactory(data, info)
#     r = factory.async_run()
#     return r
