=============================
netboy
=============================

super fast web crawler

**Note**: this package is still in beta. Use with caution !


Quickstart
----------

Install netboy::

    pip install netboy


Use logcc:

.. code-block:: python

    if __name__ == '__main__':
        setup_log('netboy')
        data = [ 'http://www.bing.com',]
        boy = NetBoy()
        boy.use_queue(
            'worker'
        ).use_spider(
            'pycurl'
        ).use_filter(
            ['url', 'title', 'code']
        ).use_workers().use_triggers([
            'test.functional.netboy.screen.print_screen'
        ])
        resp = boy.run(data)

