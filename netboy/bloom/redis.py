import random

import redis
from worker.worker import Worker


class SimpleHash:
    def __init__(self, cap, seed):
        self.cap = cap
        self.seed = seed

    def hash(self, value):
        ret = 0
        for i in range(value.__len__()):
            ret += self.seed * ret + ord(value[i])
        return ((self.cap - 1) & ret)


def simple_hash(value, seed, cap):
    ret = 0
    for i in range(value.__len__()):
        ret += seed * ret + ord(value[i])
    return ((cap - 1) & ret)


import mmh3

salt = 'salted'


def hash_func(value, seed):
    a = mmh3.hash128(salt + str(value) + '____' + str(seed))
    # print(a, '>>>')
    return a


class BloomFilter:
    def __init__(self, bit_size=25, seed_len=7):
        self.bit_size = 1 << bit_size
        self.seeds = random.sample(range(100), seed_len)  # [5, 7, 11, 13, 31, 37, 61]
        self.redis = redis.StrictRedis(host='127.0.0.1', port=6379, db=0, password='hello')

        # self.hash_func = []
        # for i in range(self.seeds.__len__()):
        #     self.hash_func.append(SimpleHash(self.bit_size, self.seeds[i]))

    def add(self, value):
        for seed in range(len(self.seeds)):
            result = hash_func(value, seed) % self.bit_size
            name = result // 8
            offset = result % 8
            self.redis.setbit(name, offset, 1)

    def has(self, value):
        for seed in range(len(self.seeds)):
            result = hash_func(value, seed) % self.bit_size
            name = result // 8
            offset = result % 8
            flag = self.redis.getbit(name, offset)
            if flag == 0:
                return False
        return True


# uid = ['alskdjflkasjdf', 'kajdsklfjlkasdf', 'lhjkkjhrwqer', 'alskdjflkasjdf']
# bf = BloomFilter()
# for e in uid:
#     bf.add(e)
#     print('added')
#
# uid.extend(['haha', 'hehe'])
# for e in uid:
#     check = bf.has(e)
#     print(e, check)


if __name__ == '__main__':
    data = [
               '1', '2', '3', '4',
           ]*1
    info = {
        'celery_worker': 'netboy.celery.tasks.coroutine_worker',
        'worker': 'netboy.celery.tasks.test',
        'celery_max_workers': 1,
        'celery_chunk_size':2,
        'chunk_size': 2,
        'queue': 'worker',
        'dummy': 'netboy.celery.tasks.dummy',
    }
    worker = Worker(mode='celery')
    resp = worker.work(data, info)
    print(resp)
