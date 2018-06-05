# coding: utf-8
import sqlite3, os
from configure import DATABASE
from configure import DEFAULT_DATABASE_NAME
from log.logger import Logger
from log.logger import getLogger

class Database(object):
    def __init__(self, database=DEFAULT_DATABASE_NAME):
        self.database = DATABASE + DEFAULT_DATABASE_NAME
        self.__logger = getLogger(Logger.STORAGE)
        self.conn = None
        self.cursor = None
        self.detect()

    def detect(self):
        self.__logger.info("start detecting the database.")

        if not os.path.exists(DATABASE):
            os.mkdir(DATABASE)

        if not os.path.exists(self.database):
            conn = sqlite3.connect(self.database, isolation_level=None, timeout=100.0)
            conn.close()

        # 创建预定义数据表
        self.__logger.info("the database detection completed.")

    '''
    开始一个新的'事务'
    '''
    def handler(self):
        self.conn = sqlite3.connect(self.db_name, isolation_level=None, timeout=100.0)
        self.cursor = self.conn.cursor()
    
    '''
    结束一个'事务'
    '''
    def commit(self):
