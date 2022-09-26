import os
import time
import json
import redis
import base64

class oop4PubRedis:
    def __init__(self, RedisIP, RedisPort, RedisPassword):
        self.DateTime = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
        self.client = redis.Redis(host = RedisIP, port = RedisPort, password = RedisPassword, db = 0)
    
    def postJsonData(self, Topic, Message):
        self.client.publish(Topic, json.dumps(Message))

    
    def postJsonBase64(self, Topic, Base64String):
        JD = {
            "uuid": f"{time.strftime('%Y%m%d%H%M%S', time.localtime())}",
            "base64string": f"{Base64String}",
            "time": f"{time.strftime('%Y/%m/%d %H:%M:%S', time.localtime())}",
        }
        self.client.publish(Topic, json.dumps(JD))


