# coding: utf-8

from downloader import Downloader
from log.logger import getLogger, Logger

'''
Seeder —— 种子下载器
'''
class Seeder(Downloader):
    
    def __init__(self, seed='https://www.lyrics.com/random.php'):
        super(Seeder, self).__init__()
        self.__origin_seed = seed

    def seed(self):
        
        r = self.request(self.__origin_seed, False)
        if r is None:
            return None
        else:
            return r.headers['location']
