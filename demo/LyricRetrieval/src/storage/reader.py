# coding: utf-8

from structure import FileSystem
from database import LyricDatabase
import json, os, math, numpy

'''
读取 IR 模型数据
'''
class ModelReader(object):

    def __init__(self):
        self.fileSystem = FileSystem()
    
    '''
    获取原来的歌词信息
    '''
    @property
    def lyrics(self):
        with open(self.fileSystem.raw_lyrics_json, "r") as raw_lyrics:
            raw_lyrics_json = json.load(raw_lyrics)
            return raw_lyrics_json

    '''
    获取所有的单词统计表
    '''
    @property
    def words(self):
        with open(self.fileSystem.words_doc_amount, "r") as words_doc_amount:
            words_doc_amount_json = json.load(words_doc_amount)
            return words_doc_amount_json
    
    '''
    获取 word 在每个文档中的tf
    '''
    def docTF(self, word):
        filepath = self.fileSystem.word_doc_tf + word + ".json"
        if not os.path.exists(filepath):
            return None
        with open(filepath, "r") as word_doc_tf:
            word_doc_tf_json = json.load(word_doc_tf)
            return word_doc_tf_json
    
    '''
    获取 word 所有的前缀词
    '''
    def prefixs(self, word):
        filepath = self.fileSystem.word_prefix_word + word + ".json"
        if not os.path.exists(filepath):
            return None
        with open(filepath, "r") as word_prefix_word:
            word_prefix_word_json = json.load(word_prefix_word)
            return word_prefix_word_json

    '''
    获取 word 的前缀词在各个文档中计数
    '''
    def prefixDocTFByIndex(self, index):
        filepath = self.fileSystem.prefix_doc_tf + index + ".json"
        if not os.path.exists(filepath):
            return None
        with open(filepath, "r") as prefix_doc_tf:
            prefix_doc_tf_json = json.load(prefix_doc_tf)
            return prefix_doc_tf_json

    '''
    获取 word 的前缀词 prefix 在各个文档中的计数
    '''
    def prefixDocTFByWord(self, word, prefix):
        word_prefix = self.prefixs(word)
        if word_prefix is None:
            return None
        index = word_prefix.get(prefix)
        if index is None:
            return None
        else:
            return self.prefixDocTFByIndex(index)
'''
IR 模型统计特征值
'''
class ModelFeature(object):
    
    def __init__(self):
        self.model_reader = ModelReader()
        self.database = LyricDatabase()
        self.keys = self.model_reader.words.keys()
    '''
    计算 word 的 idf 值
    '''
    def idf(self, word):
        feature = self.model_reader.words.get(word)
        if feature is None:
            return 0
        else:
            df_word = feature["df"]
            doc_amount = self.model_reader.fileSystem.doc_amount
            return math.log10(doc_amount/float(df_word))
    '''
    计算 word 在文档 docId 中的tf
    '''
    def tf(self, word, docId, content=True):
        doc_tf = self.model_reader.docTF(word)
        if doc_tf is None:
            tf = 0
        else:
            tf = doc_tf.get(docId)
        if tf is None:
            tf = 0
        else:
            if content:
                tf = tf["content"]
            else:
                tf = tf["title"]
        return tf

    '''
    计算 word 在文档 docId 中的权重值
    '''
    def weight(self, word, docId, normalized=False, content=True):
        idf = self.idf(word)
        if normalized:
            tf = self.normalized(word, docId, content)
        else:
            tf = self.tf(word, docId, content)
        return tf * idf
    
    '''
    计算 word 在文档 docId 的 内容中归一化之后的tf值
    '''
    def normalized(self, word, docId, content=True):
        self.database.handler()
        normalized_basic = self.database.normalized(docId, content)
        if normalized_basic == -1:
            return 0
        tf = self.tf(word, docId, content)
        self.database.commit()
        return tf / normalized_basic
    
    '''
    构建文档 docId 的文档向量
    '''
    def docVector(self, docId, normalized=False, content=True):
        vec = []
        for key in self.keys:
            vec = vec + [self.weight(key, docId, normalized, content)]
        return vec
    
    '''
    计算 docId1 和 docId2 文档向量之间的相似度
    '''
    def cosine(self, docId1, docId2, normalized=False, content=True):
        vec1 = numpy.array(self.docVector(docId1, normalized, content))
        vec2 = numpy.array(self.docVector(docId2, normalized, content))
        return numpy.dot(vec1, vec2)/(numpy.linalg.norm(vec1) * numpy.linalg.norm(vec2))
