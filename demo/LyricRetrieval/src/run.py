# coding: utf-8
from storage.structure import FileSystem

if __name__ == '__main__':
    fileSystem = FileSystem()
    fileSystem.create()
    print(fileSystem.words_doc_amount)
