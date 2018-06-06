# coding: utf-8

from structure import FileSystem
from database import LyricDatabase
import json, os, time

'''
ModelWriter
- 写入用于信息检索模型的统计数据
'''
class ModelWriter(object):
    '''
    参数:
    - doc_Id : 文档唯一标识符
    - title : dict对象,关于对歌词标题的单词计数
    - content: dict对象， 关于对内容的单词计数
    '''
    def __init__(self):
        self.fileSystem = FileSystem()

    def prepare(self, docId, title, content, title_prefixs, content_prefixs):
        self.doc_amount = self.fileSystem.doc_amount
        self.docId = docId
        self.title = title
        self.content = content
        self.title_prefixs = title_prefixs
        self.content_prefixs = content_prefixs
        self.keys = {}
        for key in self.title.keys() + self.content.keys():
            if self.keys.get(key) is None:
                self.keys[key] = 1
        self.keys = self.keys.keys()

    def write(self):
        if self.content is None or self.title is None or self.docId is None:
            return
        self.words_doc_amount()
        self.word_doc_tf()
        self.word_prefix_word()
        
    '''
    原始语料备份
    '''
    def backup(self, docId, title, content):
        if self.doc_amount == 0:
            raw_lyrics_json = {}
        else:
            with open(self.fileSystem.raw_lyrics_json, "r") as raw_lyrics:
                raw_lyrics_json = json.load(raw_lyrics)
        lyric = {'title':title, 'content':content}
        raw_lyrics_json[docId] = lyric
        with open(self.fileSystem.raw_lyrics_json, "w") as raw_lyrics:
            json.dump(raw_lyrics_json, raw_lyrics, 
                    sort_keys=True, indent=4, separators=(',', ':'))

    def words_doc_amount(self):

        if self.doc_amount == 0:
            words_doc_amount_json = {}
        else:
            with open(self.fileSystem.words_doc_amount, "r") as words_doc_amount:
                words_doc_amount_json = json.load(words_doc_amount)
        
        # 更新相关key的title计数
        for key in self.keys:
            
            temp = {"df":1}
            
            if self.title.get(key) is not None:
                temp["title"] = self.title[key]
            else:
                temp["title"] = 0

            if self.content.get(key) is not None:
                temp["content"] = self.content[key]
            else:
                temp["content"] = 0
            
            word = words_doc_amount_json.get(key)
            if word is not None:
                df = words_doc_amount_json[key].get("df")
                title = words_doc_amount_json[key].get("title")
                content = words_doc_amount_json[key].get("content")
                for c_key in temp.keys():
                    temp[c_key] = temp[c_key] + words_doc_amount_json[key][c_key]
            words_doc_amount_json[key] = temp

        # 删除旧的words_<doc_amount>.json 文件
        doc_amount = self.doc_amount + 1
        os.remove(self.fileSystem.words_doc_amount)

        with open(self.fileSystem.model_path + "words_%d.json" % doc_amount, 
                  "w") as new_words_doc_amount:
            json.dump(words_doc_amount_json, new_words_doc_amount,
                      sort_keys=True, indent=4, separators=(',', ':'))

    def word_doc_tf(self):
        for key in self.keys:
            filepath = self.fileSystem.word_doc_tf + key + ".json"
            if not os.path.exists(filepath):
                word_doc_tf_json = {}
            else:
                with open(filepath, "r") as word_doc_tf:
                    word_doc_tf_json = json.load(word_doc_tf)

            temp = {}
            
            if self.title.get(key) is not None:
                temp["title"] = self.title[key]
            else:
                temp["title"] = 0

            if self.content.get(key) is not None:
                temp["content"] = self.content[key]
            else:
                temp["content"] = 0
            

            word_doc_tf_json[self.docId] = temp
            
            with open(filepath, "w") as word_doc_tf:
                json.dump(word_doc_tf_json, word_doc_tf,
                      sort_keys=True, indent=4, separators=(',', ':'))
        return True
    
    def word_prefix_word(self):
        for key in self.keys:
            filepath = self.fileSystem.word_prefix_word + key + ".json"
            if not os.path.exists(filepath):
                word_prefix_word_json = {}
            else:
                with open(filepath, "r") as word_prefix_word:
                    word_prefix_word_json = json.load(word_prefix_word)
            
            if self.title_prefixs.get(key) is not None:
                for c_key in self.title_prefixs.get(key).keys():
                    index = word_prefix_word_json.get(c_key)
                    if index is None:
                        index = str(int(time.time() * 10000000))
                        word_prefix_word_json[c_key] = index
                    self.prefix_doc_tf(index, key, c_key)

            if self.content_prefixs.get(key) is not None:
                for c_key in self.content_prefixs.get(key).keys():
                    index = word_prefix_word_json.get(c_key)
                    if index is None:
                        index = str(int(time.time() * 10000000))
                        word_prefix_word_json[c_key] = index
                    self.prefix_doc_tf(index, key, c_key)
            
            with open(filepath, "w") as word_prefix_word:
                json.dump(word_prefix_word_json, word_prefix_word, 
                        sort_keys=True, indent=4, separators=(',', ':'))

    def prefix_doc_tf(self, index, p_key, c_key):
        filepath = self.fileSystem.prefix_doc_tf + index + ".json"
        if not os.path.exists(filepath):
            prefix_doc_tf_json = {}
        else:
            with open(filepath, "r") as prefix_doc_tf:
                prefix_doc_tf_json = json.load(prefix_doc_tf)
        try:
            title_prefix_tf = self.title_prefixs.get(p_key).get(c_key)
            if title_prefix_tf is None:
                title_prefix_tf = 0
        except AttributeError:
            title_prefix_tf = 0

        try:
            content_prefix_tf = self.content_prefixs.get(p_key).get(c_key)
            if content_prefix_tf is None:
                content_prefix_tf = 0
        except AttributeError:
            content_prefix_tf = 0
        
        if prefix_doc_tf_json.get(self.docId) is None:
            prefix_doc_tf_json[self.docId] = {"title": title_prefix_tf, "content":content_prefix_tf}
            
            with open(filepath, "w") as prefix_doc_tf:
                json.dump(prefix_doc_tf_json, prefix_doc_tf,
                        sort_keys=True, indent=4, separators=(',', ':'))
