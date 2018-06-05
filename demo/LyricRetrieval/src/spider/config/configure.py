# coding: utf-8

from log.logger import getLogger, Logger
import requests
import random
import time
import re
import os

'''
调度进程超时退出时间, 单位 : 秒
'''
TIME_OUT = 600

'''
ProxyPool —— 代理地址池
- 进一步封装 https://github.com/jhao104/proxy_pool 的接口
    - proxy : 随机获取一个proxy
    - delete : 从 proxy_pool 中删除proxy
'''
class ProxyPool(object):

    def __init__(self, \
            host='http://115.159.59.195:5010', \
            default='socks5://127.0.0.1:1084',\
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
            (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36'):

        self.__proxy_pool_host = host   # 代理池主机地址
        self.__default_proxy = default  # 当代理池为空时，默认代理
        self.__sleep_time = 1           # Try to avoid the ConnectionError
        # 访问代理池主机的Proxy
        self.__local_proxies = {'http':default,'https':default}
        # 访问代理池主机的User-Agent
        self.__local_headers = {'user-agent': user_agent}

    def proxy(self):
        logger = getLogger(Logger.PROXY)
        url = self.__proxy_pool_host + '/get'
        try:
            time.sleep(self.__sleep_time)
            proxy = requests.get(url, proxies=self.__local_proxies, \
                    headers=self.__local_headers).content

        except  requests.exceptions.ConnectionError as e:
            return self.__default_proxy
        
        re_proxy = r'^\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}:\d{1,5}$'
        if not re.match(re_proxy, proxy):
            proxy = self.__default_proxy
        else :
            proxy = 'http://' + proxy
        
        logger.info("Get a new proxy : %s." % proxy)
        return proxy

    def delete(self, proxy):

        if not isinstance(proxy, str):
            raise ValueError("The proxy must be a string!")

        re_proxy = r'^(socks5)|(http[s]?)://\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}:\d{1,5}$'

        if not re.match(re_proxy, proxy):
            raise ValueError("The proxy must like socks5|http|https://xxx.xxx.xxx.xxx:xxxx")

        if(proxy == self.__default_proxy or not proxy):
            return

        url = self.__proxy_pool_host + '/delete'
        params = {'proxy':proxy.split('/')[2]}

        retry_count = 5
        while(retry_count):
            try:
                time.sleep(self.__sleep_time)
                r = requests.get(url, params=params, \
                    proxies=self.__local_proxies, headers=self.__local_headers)
                break

            except requests.exceptions.ConnectionError as e:
                retry_count = retry_count - 1

'''
UserAgentPool
- 读取 user-agent.config 的客户端配置, 维持一个客户端池
- user_agent : 随机获取一个客户端配置
'''
class UserAgentPool(object):

    def __init__(self):
        self.__user_agent_pool = []
        current_dir = os.path.dirname(os.path.realpath(__file__))
        self.__user_agent_config = current_dir + os.sep + 'user-agent.config'
        with open(self.__user_agent_config, 'r') as config:
            for line in config.readlines():
                self.__user_agent_pool.append(line.strip())
        
    # 随机返回一个新的 User-Agent
    def user_agent(self):
        random.seed(int(time.time()))
        length = len(self.__user_agent_pool)
        return self.__user_agent_pool[random.randint(0, length - 1)]
