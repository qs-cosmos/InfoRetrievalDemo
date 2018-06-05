# coding:utf-8

from bs4 import BeautifulSoup
from log.logger import getLogger, Logger
from storage.structure import FileSystem
from storage.writer import ModelWriter
from preprocess.linguistics import Linguistics
from spider.message.message import MessageQueue
import os, abc, codecs, re

'''
Analyser —— 爬虫解析器
- Analyser 用于解析html文档, 并将解析结果写入文件或数据库中。
- Analyser 通过调用 Parser 和 Database 的接口(parse, write)进行 解析 和 写入
- 通过改变继承自 Parser 和 Database 的子类, 可实现不同的解析过程和写入对象
'''
class Analyser(object):

    def __init__(self, parser, database):
        
        if not isinstance (database, Database):
            raise ValueError('The database must be a subclass of Database')

        if not isinstance (parser, Parser):
            raise ValueError('The parser must be a subclass of Parser')
        
        self.__logger = getLogger(Logger.ANALYSER)
        self.__parser = parser
        self.__database = database
    
    def resolve(self, html):
        self.__logger.info('...start parsing...')
        result = self.__parser.parse(html, )
        self.__logger.info('....stop parsing...')
        self.__logger.info('...start exporting...')
        self.__database.write(result)
        self.__logger.info('....stop exporting...')

'''
Database 
- Database 是一个抽象类
- Database 的子类必须实现write方法
'''
class Database(object):
    
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def write(self, data):
        return

'''
IRModel
- IRModel 继承自Database
- IRModel 将Parser得到的结果进行统计分析, 构建信息检索模型的数据基础
'''
class IRModel(Database):
    def __init__(self, prefix="http://www.lyrics.com/lyric/"):
        self.__file_system = FileSystem()
        self.__logger = getLogger(Logger.ANALYSER)
        self.__linguistics = Linguistics()
        self.__seed_prefix = prefix
        self.__model_writer = ModelWriter()

    def write(self, data): 
        self.__logger.info("...IRModel Test...")

        if data is None:
            return

        if not isinstance(data, dict):
            raise ValueError("The data to JsonFile must be json format!")
        
        seed = data['seed']
        title = data['title']
        docId = self.getId(seed)
        title_words = self.wordsCount(self.__linguistics.words(title))
        content_words = self.wordsCount(self.__linguistics.words(data['content']))
        self.__model_writer.prepare(docId, title_words, content_words)
        self.__model_writer.write()
        self.__logger.info("...IRModel Test Finished...")
        
    def getId(self, seed):
        return re.subn(self.__seed_prefix, "", seed)[0]
    
    def wordsCount(self, words):
        words_count = {}
        for word in words:
            frequency = words_count.get(word)
            if frequency is None:
                frequency = 0
            words_count[word] = frequency + 1
        return words_count

'''
JsonFile
- JsonFile 继承自Database
- JsonFile 将Parser得到的结果转换成 Json 格式, 并写入到.json文件中
'''
class JsonFile(Database):
    
    def __init__(self, path='json/'):
        self.__path = path
        self.__logger = getLogger(Logger.ANALYSER)
        if not os.path.exists(self.__path):
            os.mkdir(self.__path)

    def write(self, data):
        
        if data is None:
            return

        if not isinstance(data, dict):
            raise ValueError("The data to JsonFile must be json format!")
        try:
            toJsonTemplate ='{\n\t"title": "$title",\n' \
                            '\t"paragraphs": ['\
                            '$paragraph'\
                            '\n]}'
            paragraphTemplate = '\n\t{"sentences":[\n$sentences\n\t]}'
            
            title = data['title'].strip()
            
            paragraph_list = data['content'].replace('\r', '').split('\n\n')
            
            toJson = toJsonTemplate.replace('$title',  title)
            paragraphs = ''
            for paragraph in paragraph_list:
                
                paragraph = '"' + paragraph.replace('\n', '","') + '"'

                paragraphs += ',' + paragraphTemplate.replace('$sentences', paragraph)
            toJson = toJson.replace('$paragraph', paragraphs)

            output_path = self.__path + title + '.json'
            if not os.path.exists(output_path) :
                os.mknod(output_path)

            with codecs.open(output_path, 'w', 'utf-8') as json_file:
                json_file.write(toJson)
        except Exception as e:
            self.__logger.error('%s' % str(e))
            self.__logger.error('%s' % str(data))
'''
Parser 
针对不同的网页内容和需求, 存在不同的解析策略
- Parser 是一个抽象类
- Parser 的子类必须实现parse方法
'''
class Parser(object):

    __metaclass__ = abc.ABCMeta
    
    '''
    content_type : 文本内容格式
    parser : 采用的解析器
    '''
    def __init__(self, content_type='html', parser='lxml'):
        self.content_type = content_type
        self.parser = parser

    @abc.abstractmethod
    def parse(self, text):
        return

'''
LyricParser
- 网页来源: www.lyrics.com
- 解析结果: 
    - 类型 : dict
    - keys : 
        - title —— 歌名
        - content —— 歌词
'''
class LyricParser(Parser):

    def __init__(self):
        super(LyricParser, self).__init__()
        self.__logger = getLogger(Logger.ANALYSER)

    def parse(self, text):
        if self.content_type == 'html':
            texts = text.split('$S$E$E$D$')
            soup = BeautifulSoup(texts[1], self.parser)
            title = soup.find(id='lyric-title-text')
            content = soup.pre
            if title is None or content is None:
                self.__logger.info("Lyric parser gets nothing.")
                return None

            return { 'title':title.get_text(),\
                     'content':content.get_text(),\
                     'seed': texts[0]}
