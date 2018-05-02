#-*- coding:utf-8 -*-
import os
import re
import json
from nltk.stem import PorterStemmer

class Dictionary(object):
    '''
    class dictionary
    '''

    def __init__(self):
        self.lyrics_path = "data/lyrics/"
        self.stop_words = ['a', 'am', 'an', 'is', 'are',
                           'as', 'at', 'and', 'be']

        self.regex = "\n*\t*( )*[,，\.。、~\_\-：:《》！!<>?？;；'\"'‘’“”/\\\[\]【】「」\{\}\(\)（）]*( )*\t*\n*"
        self.ps = PorterStemmer()

    def save_file_idx(self, cursor):
        '''
        get the filenames of lyrics and
        save into database
        '''
        self.lyric_files = os.listdir(self.lyrics_path)

        # create table
        cursor.execute('CREATE TABLE IF NOT EXISTS lyric_files (file_id INTEGER PRIMARY KEY, file_name text)')

        # insert into database
        for fidx, lyric_file in enumerate(self.lyric_files):
            cursor.execute('INSERT INTO lyric_files (file_id, file_name) VALUES (?, ?)', (fidx, lyric_file))


    def word_split(self, sentence):
        '''
        split a sentence into words,
        spliter: ' ', ',', '.'
        :return: a list of words
        '''
        words = re.split(r',| ', sentence)

        # reduce regex
        words = [re.subn(self.regex, "", word)[0] for word in words]

        # to lower case
        words = [word.lower() for word in words if word != u'']

        # stop words table
        words = [word for word in words if word not in self.stop_words]

        # stem words
        words = [self.ps.stem(word) for word in words]

        return words


    def gen_raw_words(self):
        '''
        get all words from lyrics files
        :return: lists of words
        '''
        words = []
        for fidx, lyric_file in enumerate(self.lyric_files):
            with open(self.lyrics_path + lyric_file) as fin:
                sample = json.load(fin)
                sample_words = []
                paragraphs = sample['paragraphs']
                for paragraph in paragraphs:
                    sentences = paragraph['sentences']
                    for sentence in sentences:
                        sample_words.extend(self.word_split(sentence))
                words.append(sample_words)
        self.words = words

    def gen_vocab(self):
        '''
        generate vocabulary from words
        :param words:
        '''
        vocab = set()
        for lyric_words in self.words:
            for word in lyric_words:
                vocab.add(word)
        self.vocab = sorted(vocab)


    def words_clean(self):
        '''
        clean raw words
        :return: cleaned words
        '''
        # TODO
        cleaned_words = []
        return cleaned_words


    def save_word_count(self, cursor):
        '''
        count words occurance and save to database
        :return:
        '''
        # create table
        cursor.execute('CREATE TABLE IF NOT EXISTS word_count (word text PRIMARY KEY, count int)')
        cursor.execute('CREATE TABLE IF NOT EXISTS word_file_count (word text, file_id int, count int, PRIMARY KEY(word, file_id))')

        for vocab_word in self.vocab:
            # total count of occurance of a vocab_word
            count = 0

            for lidx, lyric_words in enumerate(self.words):
                cnt = lyric_words.count(vocab_word)
                count += cnt
                if cnt > 0:
                    cursor.execute('INSERT INTO word_file_count (word, file_id, count) VALUES (?, ?, ?)',
                                (vocab_word, lidx, cnt))

            cursor.execute('INSERT INTO word_count (word, count) VALUES (?, ?)',
                           (vocab_word, count))