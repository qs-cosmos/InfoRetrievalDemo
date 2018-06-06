# coding: utf-8
import sqlite3, os
from configure import DATABASE
from configure import DEFAULT_DATABASE_NAME
from log.logger import Logger
from log.logger import getLogger

class LyricDatabase(object):
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
        self.__logger.info("..detect the lyric table..")
        self.__create_table_lyric()
        self.__logger.info("..the lyric table detection completed..")
        self.__logger.info("the database detection completed.")

    '''
    开始一个新的'事务'
    '''
    def handler(self):
        self.conn = sqlite3.connect(self.database, isolation_level=None, timeout=100.0)
        self.cursor = self.conn.cursor()
    
    '''
    结束一个'事务'
    '''
    def commit(self):
        if self.cursor is not None:
            self.cursor.close()
            self.cursor = None

        if self.conn is not None:
            self.conn.commit()
            self.conn.close()
            self.conn = None
    
    '''
    创建 lyric table
    '''
    def __create_table_lyric(self):
        self.handler()
        sql = '''
        CREATE TABLE IF NOT EXISTS lyric (
        id VARCHAR(20) PRIMARY KEY,
        url VARCHAR(35),
        title_word_amount INT,
        title_normalized DOUBLE,
        content_word_amount INT,
        content_normalized DOUBLE
        );
        '''
        try:
            self.cursor.execute(sql)
        except Exception as e:
            self.__logger.warning("Exception in creating table lyric. Caused by: %s" %  str(e))
        self.commit() 
    
    '''
    返回值:
    - True : ok
    - False : 插入失败
    '''
    def insert_lyric(self, docId, url, title_word_amount, title_normalized, 
                    content_word_amount, content_normalized):
        if self.cursor is None or self.conn is None:
            return False
        try:
            sql = '''INSERT INTO lyric(id, url, title_word_amount, title_normalized, 
                   content_word_amount, content_normalized) values(?, ?, ?, ?, ?, ?)'''
            self.cursor.execute(sql, (docId, url, title_word_amount, title_normalized ,content_word_amount, content_normalized))
            return True
        except Exception as e:
            self.__logger.warning("Exception in the insert lyric operation. Caused by: %s" % str(e))
            return False
    
    '''
    查询 docId 对应的歌词基本信息
    '''
    def lyric(self, docId):
        if self.cursor is None or self.conn is None or docId is None:
            return None
        try:
            sql = "SELECT * FROM lyric WHERE id=?"
            self.cursor.execute(sql, (docId,))
            values = self.cursor.fetchall()
            if len(values) == 0:
                return None
            else:
                return values[0]
        except Exception as e:
            self.__logger.warning("Exception in the select lyric operation. Caused by: %s" % str(e))
            return None
    
    '''
    查询 多个 歌词基本信息
    docIds
    - [docId1, docId2,...]
    '''
    def lyrics(self, docIds):
        if self.cursor is None or self.conn is None or len(docIds) == 0 or docIds is None:
            return None
        try:
            params = '('
            for i in range(0, len(docIds) - 1):
                params = params + '?,'
            params = params + '?)'
            sql = "SELECT * FROM lyric WHERE id in %s" % params
            self.cursor.execute(sql, tuple(docIds))
            values = self.cursor.fetchall()
            return values
        except Exception as e:
            self.__logger.warning("Exception in the select lyrics operation. Caused by: %s" % str(e))
            return None

    '''
    查询 docId 对应的单词总数
    '''
    def wordCount(self, docId, content=True):
        if self.cursor is None or self.conn is None or docId is None:
            return 0
        try:
            if content:
                sql = "SELECT content_word_amount FROM lyric WHERE id=?"
            else:
                sql = "SELECT title_word_amount FROM lyric WHERE id=?"
            self.cursor.execute(sql, (docId,))
            values = self.cursor.fetchall()
            if len(values) == 0:
                return 0
            else:
                return values[0][0]
        except Exception as e:
            self.__logger.warning("Exception in the select word count operation. Caused by: %s" % str(e))
            return -1

    def wordCounts(self, docIds, content=True):
        if self.cursor is None or self.conn is None:
            return None
        try:
            if docIds is None:
                params=''
            else:
                params = ' WHERE id in ('
                for i in range(0, len(docIds) - 1):
                    params = params + '?,'
                params = params + '?)'

            if content:
                sql = "SELECT id,content_word_amount FROM lyric %s" % params
            else:
                sql = "SELECT id,title_word_amount FROM lyric %s"% params

            if docIds is None:
                self.cursor.execute(sql)
            else:
                self.cursor.execute(sql, tuple(docIds))
            
            values = self.cursor.fetchall()

            if len(values) == 0:
                return None
            else:
                return values
        except Exception as e:
            self.__logger.warning("Exception in the select word count operation. Caused by: %s" % str(e))
            return None

    def totalWordCount(self, content=True):
        if self.cursor is None or self.conn is None:
            return 0
        try:
            if content:
                sql = "SELECT sum(content_word_amount) FROM lyric"
            else:
                sql = "SELECT sum(title_word_amount) FROM lyric"
            self.cursor.execute(sql)
            values = self.cursor.fetchall()
            if len(values) == 0:
                return 0
            else:
                return values[0][0]
        except Exception as e:
            self.__logger.warning("Exception in the select total word count operation. Caused by: %s" % str(e))
            return -1
    
    '''
    查询 docId 对应tf归一化底数
    '''
    def normalized(self, docId, content=True):
        if self.cursor is None or self.conn is None or docId is None:
            return -1
        try:
            if content:
                sql = "SELECT content_normalized FROM lyric WHERE id=?"
            else:
                sql = "SELECT title_normalized FROM lyric WHERE id=?"
            self.cursor.execute(sql, (docId,))
            values = self.cursor.fetchall()
            if len(values) == 0:
                return -1
            else:
                return values[0][0]
        except Exception as e:
            self.__logger.warning("Exception in the select normalized operation. Caused by: %s" % str(e))
            return -1
    
    def docAmount(self):
        self.handler()
        try:
            sql = "SELECT COUNT(id) FROM lyric"
            values = self.cursor.execute(sql)
            return int(values[0][0])
        except Exception as e:
            self.__logger.warning("Exception in the insert lyric operation. Caused by: %s" % str(e))
            return 0
        finally:
            self.commit()
