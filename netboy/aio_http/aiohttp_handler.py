from netboy.aio_http.aiohttp_factory import AIOHttpFactory


async def aiohttp_handler(data, info):
    factory = AIOHttpFactory(data, info)
    r = await factory.run()
    return r
