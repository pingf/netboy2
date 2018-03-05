def filter_chrome_result(data, driver):
    filter_map = {
        'url': lambda: data.get('url'),
        'effect': lambda: driver.current_url,
        'data': lambda: driver.page_source,
        'title': lambda: driver.title,
        'code': lambda: data.get('fake_code'),
        'time': lambda: data.get('time'),
        'screen': lambda: driver.get_screenshot_as_base64(),
        # 'cookies': lambda: driver.get_cookies(),
        'cookie': lambda: driver.get_cookies(),
    }
    result = {}
    chrome_filter = data.get('filter')
    if not chrome_filter:
        chrome_filter = ['url', 'effect', 'time', 'code', 'title']
    for f in chrome_filter:
        if f in filter_map.keys():
            result[f] = filter_map[f]()
    return result


def get_result(data, driver):
    result = {'state': 'normal', 'spider': 'chrome'}
    chrome_result = filter_chrome_result(data, driver)
    result.update(chrome_result)
    return result
