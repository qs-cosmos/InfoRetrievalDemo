# coding: utf-8

from downloader import Downloader
from log.logger import getLogger, Logger
from spider.message.message import MessageQueue
'''
Fisher —— 网页抓取
'''
class Fisher(Downloader):

    def fish(self, seed):
        r = self.request(seed)
        if r is None:
            return None
        else:
            return r.text


