from aiohttp import web
import sys

from netboy.netboy import NetBoy
from netboy.remote.auth import db, User


async def handle_post(request):
    resp = await request.json()
    print(resp)
    response = web.Response(text=str(resp))
    return response


async def handle_register(request):
    resp = await request.json()
    user = resp.get('user')
    password = resp.get('password')
    if not user or not password:
        response = web.Response(text='user and password can not be none', status=422)
        return response

    group = resp.get('group', 'default')

    print(user, 'registering...')

    resp = User.add(user=user, password=password, group=group)
    response = web.Response(text=str(resp))
    return response


async def handle_run(request):
    resp = await request.json()
    try:
        info = resp['info']
        auth = info.get('auth')
        data = resp['data']

        user = auth.get('user')
        password = auth.get('password')
        hashed = User.hashit(password)

        udb = User.query(user=user)
        user_db = udb.get('user')
        password_db = udb.get('password')
    except Exception as e:
        text = 'bad params! type: ' + str(type(e)) + ' desc: ' + str(e)
        response = web.Response(text=text, status=422)
    else:
        if user == user_db and hashed == password_db:
            boy = NetBoy()
            boy.use_info(info)
            resp = boy.run(data)
            text = str(resp)
            response = web.Response(text=text, status=200)
        else:
            response = web.Response(text='forbidden', status=403)

    return response


if __name__ == '__main__':

    db.generate_mapping(create_tables=True, check_tables=True)

    app = web.Application()
    app.router.add_route('POST', '/run', handle_run)
    app.router.add_route('POST', '/register', handle_register)
    app.router.add_route('POST', '/post', handle_post)

    if len(sys.argv) >= 1:
        port = int(sys.argv[1])
    else:
        port = 8080
    web.run_app(app, port=port)
