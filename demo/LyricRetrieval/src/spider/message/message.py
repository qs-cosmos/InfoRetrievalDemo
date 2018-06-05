# coding:utf-8

import redis

'''
MessageQueue —— 消息队列
- seed : 种子队列
- html : html队列
- repeat : 去重队列
'''
class MessageQueue(object):

    def __init__(self, host='127.0.0.1', port=6379, decode_responses=True):
        self.__connection_pool = redis.ConnectionPool(host=host, \
                port=port, decode_responses=decode_responses)
        self.__seed_redis = redis.Redis(connection_pool = self.__connection_pool)
        self.__html_redis = redis.Redis(connection_pool = self.__connection_pool)
        self.__repeat_redis = redis.Redis(connection_pool = self.__connection_pool)
        self.__seed_list = 'seeds'
        self.__html_list = 'htmls'
        self.__repeat_set = 'repeat'

    @property
    def seed(self):
        return self.__seed_redis.lpop(self.__seed_list)
    
    @seed.setter
    def seed(self, seed):
        self.__seed_redis.rpush(self.__seed_list, seed)

    @property
    def html(self):
        return self.__html_redis.lpop(self.__html_list)

    @html.setter
    def html(self, html):
        self.__html_redis.rpush(self.__html_list, html)
    
    def exists(self, seed):
        if seed is None:
            return False
        return self.__repeat_redis.sismember(self.__repeat_set, seed)

    def repeat(self, seed):
        self.__repeat_redis.sadd(self.__repeat_set, seed)

    # 清除所有数据
    def clear(self):
        self.__seed_redis.delete(self.__seed_list)
        self.__html_redis.delete(self.__html_list)
        self.__html_redis.delete(self.__repeat_set)

