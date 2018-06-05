# coding: utf-8

import os
import re
from configure import GEN
from configure import DATABASE
from configure import MODEL
from log.logger import getLogger, Logger
'''
IR 数据存储文件系统
'''
class FileSystem(object):
    def __init__(self):
        self.__logger = getLogger(Logger.STORAGE)
        self.__gen_path = GEN
        self.database_path = DATABASE
        self.model_path = MODEL
        self.word_doc_tf = self.model_path + "word_doc_tf/"
        self.word_prefix_word = self.model_path + "word_prefix_word/"
        self.prefix_doc_tf = self.model_path + "prefix_doc_tf"
        
        self.detect()

    @property
    def words_doc_amount(self):

        word_doc_count = reduce( lambda x, y: x + y, \
                map( lambda x : x if re.match(r"words_\d*.json", x) else '', \
                os.listdir(self.model_path)))
        return self.model_path + word_doc_count
    
    @property
    def doc_amount(self):
        return int(re.subn(".*words_|.json", "", self.words_doc_amount)[0])

    '''
    sqlite 数据库
    '''
    def database(self):
        if not os.path.exists(self.database_path):
            os.mkdir(self.database_path)
    '''
    IR 数据存储结构
    '''
    def model(self, path="model/"):
        words_doc_amount = self.model_path + "words_0.json"
        if not os.path.exists(self.model_path):
            os.mkdir(self.model_path)

        if not os.path.exists(self.word_doc_tf):
            os.mkdir(self.word_doc_tf)
        
        if not os.path.exists(self.word_prefix_word):
            os.mkdir(self.word_prefix_word)
        
        if not os.path.exists(self.prefix_doc_tf):
            os.mkdir(self.prefix_doc_tf)

        if not reduce(lambda x, y : x or y, \
                map (lambda x: re.match(r"words_\d*.json", x), os.listdir(self.model_path))):
            os.mknod(words_doc_amount)
    
    def detect(self):
        self.__logger.info("start detecting the storage file system")
        if not os.path.exists(self.__gen_path):
            os.mkdir(self.__gen_path)
        self.database()
        self.model()
        self.__logger.info("the storage file system is completed")
