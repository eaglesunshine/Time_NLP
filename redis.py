# -*- coding: utf-8 -*-
# @author: linwanpeng
# @software: PyCharm
# @file: redis.py
# @time: 2022/8/10 22:28

import json

from redis import StrictRedis


class RedisClient:
    def __init__(self):
        self.redis_conn = StrictRedis(host="127.0.0.1", port=6379, db=0, password="")

    def set(self, k, v):
        return self.redis_conn.set(k, json.dumps(v))

    def setex(self, name, time, value):
        return self.redis_conn.setex(name, time, value)

    def get(self, k):
        val = self.redis_conn.get(k)
        if val:
            return val.decode("utf-8")
        return ""
