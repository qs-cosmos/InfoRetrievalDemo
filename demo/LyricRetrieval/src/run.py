# coding: utf-8
from storage.structure import FileSystem
from storage.writer import ModelWriter
from storage.reader import ModelReader
from storage.reader import ModelFeature
from storage.database import LyricDatabase
from spider.analyse.analyser import IRModel
from query.query import LanguageModel

if __name__ == '__main__':
    '''
    writer = ModelWriter()
    writer.prepare('121', {"a" : 1, "b":2, "p":3}, {"c":2, "k":4, "f":6}, {'b':{'a':1, 'p':1}, 'p':{'p':1, 'b':2}}, {'b':{'f':2, 'p':3}, 'f':{'k':4, 'c':2}})
    writer.write()
    print(writer.fileSystem.doc_amount)
    '''
    
    '''
    database = LyricDatabase()
    database.handler()
    # database.insert_lyric('121', 'www.lyrics.com/lyrics/121', 111, 111)
    print database.lyrics(["6402429", "15429546"])
    database.commit()
    '''
    '''
    reader = ModelReader()
    print reader.words["time"]
    print reader.docTF("time").get("26230677")
    # print reader.prefixs("love")
    
    '''

    '''
    feature = ModelFeature()
    print feature.idf("time")
    print feature.weight("time", "26230677", True)
    print feature.normalized("time", "26230677")
    print feature.cosine("26230677", "15821371")
    '''

    '''
    model = IRModel()
    print model.wordsCount(['a', 'b', 'c', 'd', 'f', 'b'])
    '''
    model = LanguageModel()
    print model.query("see you")
