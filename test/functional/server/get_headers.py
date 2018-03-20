from aiohttp import web

async def handle(request):

    text = "Hello, World"
    print(request.headers)
    response = web.Response(text=text)
    return response

app = web.Application()
app.router.add_get('/', handle)
app.router.add_get('/{name}', handle)

web.run_app(app, port=8082)