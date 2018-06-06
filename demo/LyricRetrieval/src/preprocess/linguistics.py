# coding: utf-8

from configure import STOPWORDS
from configure import FILTER
from configure import SPLITER
import re
from nltk.stem import PorterStemmer

'''
Linguistics
- 对文本内容进行语言学预处理
    - 词条化
    - 去除停用词和特殊符号
    - 词干还原
'''
class Linguistics(object):
    def __init__(self):
        self.__word_filter = FILTER
        self.__stop_words = STOPWORDS
        self.__spliter = SPLITER
        self.__stem = PorterStemmer()
    '''
    split a sentence into words,
    spliter: ' ', ',', '.'
    :return: a list of words
    '''
    def words(self, content, stem=True):
        # 词条化
        words = re.split(self.__spliter, content)
        
        # 特殊符号过滤
        words = [re.subn(self.__word_filter, "", word)[0] for word in words]

        # 单词归一化
        words = [word.lower() for word in words if word != u'']

        # 停用词
        words = [word for word in words if word not in self.__stop_words]

        # 词干还原 (stemming)
        if stem:
            words = [self.__stem.stem(word) for word in words]

        return words
