# coding: utf-8
from storage.structure import FileSystem
from storage.writer import ModelWriter

if __name__ == '__main__':
    writer = ModelWriter()
    writer.prepare('121', {"a" : 1, "b":2, "p":3}, {"c":2, "k":4, "f":6})
    writer.write()
    print(writer.fileSystem.doc_amount)
