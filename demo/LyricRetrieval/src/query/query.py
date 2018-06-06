# coding: utf-8

from storage.reader import ModelReader
from storage.reader import ModelFeature
from storage.database import LyricDatabase
from preprocess.linguistics import Linguistics
import time
class LanguageModel(object):

    def __init__(self):
        self.reader = ModelReader()
        self.feature = ModelFeature()
        self.database = LyricDatabase()
        self.linguistics = Linguistics()

    def prepare(self, content=True):
        self.database.handler()

        self.words = self.reader.words

        temp = self.database.wordCounts(None, content)

        self.doc_word_counts = {}
        for doc_word_count in temp:
            self.doc_word_counts[doc_word_count[0]] = doc_word_count[1]
        self.model_words_count = self.database.totalWordCount()

        self.database.commit()

    '''
    参数
    - content : 查询内容
    - 返回值 : 经评分排序后的三元组 <title, url, id>
    '''
    def query(self, content):
        doc_content_probability = self.probability(content, "content")

        doc_array = []

        for key in doc_content_probability.keys():
            probability = doc_content_probability[key]
            doc_array = doc_array + [(key , probability)]

        doc_array.sort(key = lambda x: -x[1])
        
        return doc_array
 
    def probability(self, content, contentType):
        if contentType == "content":
            self.prepare()
        else:
            self.prepare(False)

        words = self.linguistics.words(content)
        # 过虑模型中不存在的word
        words = [word for word in words if self.words.get(word) is not None]
        prefix = None
        doc_probability = {}
        global_probability = 1
        for word in words:
            # 获取包含word前缀为prefix的全部文档
            # 当结果为 None 时, 说明 prefix 与 word 相互独立
            prefix_doc_tf = self.reader.prefixDocTFByWord(word, prefix)
            if prefix_doc_tf is None:
                model_word_count = self.words[word][contentType]
                model_word_probability = model_word_count / float(self.model_words_count)
                # 获取 包含 word 的所有文档
                word_doc_tf = self.reader.docTF(word)
                
                # 先处理 doc_probability 中的文档
                for key in doc_probability.keys():
                    tf = word_doc_tf.get(key)
                    if tf is not None:
                        p =  tf[contentType] / float(self.doc_word_counts.get(key))
                    else:
                        p = model_word_probability
                    doc_probability[key] = doc_probability[key] * p
                
                # 再处理新得到的文档
                for key in word_doc_tf.keys():
                    if doc_probability.get(key) is None:
                        tf = word_doc_tf.get(key)[contentType]
                        p = tf / float(self.doc_word_counts.get(key))
                        doc_probability[key] = global_probability * p
            else:
                word_prefix_count = 0

                for key in prefix_doc_tf.keys():
                    word_prefix_count= word_prefix_count + prefix_doc_tf[key][contentType]

                model_word_count = self.words[word][contentType]
                model_word_probability = word_prefix_count / float(model_word_count)
                word_doc_tf = self.reader.docTF(word)

                # 先处理 doc_probability 中的文档
                for key in doc_probability.keys():
                    
                    tf = prefix_doc_tf.get(key)
                    if tf is not None:
                        p = tf[contentType] / float(word_doc_tf[key][contentType])
                    else:
                        tf = word_doc_tf.get(key)
                        if tf is not None:
                            p = tf[contentType] / float(self.doc_word_counts.get(key))
                        else:
                            p = model_word_probability
                    doc_probability[key] = doc_probability[key] * p

                # 处理新得到的文档
                for key in prefix_doc_tf.keys():
                    if doc_probability.get(key) is None:
                        tf = prefix_doc_tf[key][contentType]
                        p = tf / float(word_doc_tf[key][contentType])
                        doc_probability[key] = global_probability * p
            
            global_probability = global_probability * model_word_probability
            prefix = word

        return doc_probability
    
