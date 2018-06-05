# coding: utf-8

from structure import FileSystem
import json, os

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

    def prepare(self, docId, title, content):
        self.docId = docId
        self.title = title
        self.content = content
        self.keys = {}
        for key in self.title.keys() + self.content.keys():
            if self.keys.get(key) is None:
                self.keys[key] = 1
    '''
    返回值: 
    - True : ok
    - False : fail
    '''
    def write(self):
        if self.content is None or self.title is None or self.docId is None:
            return False
        if self.word_doc_tf():
            self.words_doc_amount()
        else:
            return False

    def words_doc_amount(self):

        if self.fileSystem.doc_amount == 0:
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
        doc_amount = self.fileSystem.doc_amount + 1
        os.remove(self.fileSystem.words_doc_amount)

        with open(self.fileSystem.model_path + "words_%d.json" % doc_amount, 
                  "w") as new_words_doc_amount:
            json.dump(words_doc_amount_json, new_words_doc_amount,
                      sort_keys=True, indent=4, separators=(',', ':'))
    '''
    返回值
    - True : 正常
    - False : docId重复
    '''
    def word_doc_tf(self):
        for key in self.keys:
            filepath = self.fileSystem.word_doc_tf + key + ".json"
            if not os.path.exists(filepath):
                word_doc_tf_json = {}
            else:
                with open(filepath, "r") as word_doc_tf:
                    word_doc_tf_json = json.load(word_doc_tf)
            if word_doc_tf_json.get(self.docId) is not None:
                print("False")
                return False

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
