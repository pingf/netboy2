import hashlib
from datetime import datetime
from logging import Handler

from pony.orm import Database, Required, db_session, select

db = Database(provider='sqlite', filename='/tmp/netboy_auth.sqlite', create_db=True)


class User(db.Entity):
    create_at = Required(datetime, sql_default='CURRENT_TIMESTAMP', default=lambda: datetime.utcnow())
    user = Required(str, unique=True)
    password = Required(str)
    group = Required(str)

    @staticmethod
    @db_session
    def add(user, password, group='default'):
        user = User.query(user)
        if not user:
            User(user=user, password=User.hashit(password), group=group)

    @staticmethod
    @db_session
    def query(user):
        user = select(u for u in User if u.user == user).first()
        if user:
            return {
                'user': user.user,
                'password': user.password,
                'group': user.group,
            }
        return None

    @staticmethod
    def hashit(data, digest_size=32, key=b'netboy', items=[b'netboy', b'spider']):
        h = hashlib.blake2b(bytes(data, 'utf8'), digest_size=digest_size, key=key)
        for item in items:
            h.update(item)
        return h.hexdigest()
