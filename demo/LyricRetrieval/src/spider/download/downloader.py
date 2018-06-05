# coding: utf-8
import requests
from spider.config.configure import ProxyPool
from spider.config.configure import UserAgentPool
from log.logger import getLogger, Logger
import codecs
import time

'''
Downloader —— 爬虫下载器

下载策略 : 
    - 设置 代理 和 客户端类型 模拟正常用户的访问操作
        - proxy : https://github.com/jhao104/proxy_pool
        - user-agent : user-agent.config
        - 每个 proxy 和 user-agent 使用超过预值时, 重新进行选取
    - 网页下载 : requests
'''
class Downloader(object):

    def __init__(self):
        self.__proxy_pool = ProxyPool()
        self.__user_agent_pool = UserAgentPool()

        self.__max_mask_count = 40
        self.__mask_count = self.__max_mask_count
        self.__config()
        self.__logger = getLogger(Logger.DOWNLOADER)

    def __config(self):
        self.__proxy = self.__proxy_pool.proxy()
        self.__user_agent = self.__user_agent_pool.user_agent()

        self.__proxies = {
            'http':self.__proxy,
            'https':self.__proxy
        }
        self.__headers = {
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding':'gzip, deflate, br',
            'Accept-Language':'zh-CN,zh;q=0.9',
            'Connection':'keep-alive',
            'Host':'www.lyrics.com',
            'Referer':'https://www.lyrics.com/',
            'Upgrade-Insecure-Requests':'1',
            'User-Agent':self.__user_agent
        }

    def request(self, seed, allow_redirects=True):
        
        self.__logger.info('Start requesting %s ' % seed)
        if not isinstance(seed, str):
            raise ValueError("The seed must be a string!")

        if (self.__mask_count):
            self.__mask_count = self.__mask_count - 1
        else:
            self.__mask_count = self.__max_mask_count
            self.__config()

        '''
        - 若retry_count == 0, 说明当前 proxy 和 user-agent可能存在问题
        - 重置 proxy
            - 从 proxy_pool 中删除当前 proxy
            - 从 proxy_pool 中获取一个 新的proxy
        - 重置 user-agent
        - 重置 proxy 和 user-agent 使用计数
        - 再进行一次 retry 
        '''
        retry_count = 2
        while (retry_count) :
            try:
                time.sleep(1)
                r =  requests.get(seed, proxies=self.__proxies, \
                        headers=self.__headers, allow_redirects=allow_redirects)
                self.__logger.info('Request %s successfully.' % seed)
                return r

            except requests.exceptions.RequestException as e:
                retry_count  = retry_count - 1
                self.__logger.error( '%s' % (str(e)))
                self.__logger.warn('The %dth Retry to request %s.' % (retry_count, seed))

        self.__proxy_pool.delete(self.__proxy)
        self.__config()
        self.__mask_count = self.__max_mask_count
        
        retry_count = 2
        while (retry_count) :
            try:
                time.sleep(1)
                r =  requests.get(seed, proxies=self.__proxies, \
                        headers=self.__headers, allow_redirects=allow_redirects)
                self.__logger.info('Request %s successfully.' % seed)
                return r

            except requests.exceptions.RequestException as e:
                retry_count  = retry_count - 1
                self.__logger.error( '%s' % (str(e)))
                self.__logger.warn('The %dth Retry to request %s.' % (retry_count, seed))

        self.__logger.warn('Failed to request %s.' % seed)
        return None

