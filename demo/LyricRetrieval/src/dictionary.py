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
        self.lyrics_path = "data/lyrics/raw/"
        self.processed_lyrics_path = "data/lyrics/processed/"
        self.stop_words = [u'a', u'am', u'an', u'is', u'are',
                           u'as', u'at', u'and', u'be']

        self.regex = "\n*\t*( )*[,，\.。、~\_\-：:《》！!<>?？;；'\"'‘’“”/\\\[\]【】「」\{\}\(\)（）]*( )*\t*\n*"
        self.ps = PorterStemmer()

    def save_file_idx(self, cursor):
        '''
        get the filenames of lyrics and
        save into database
        '''

        self.lyric_files = os.listdir(self.lyrics_path)
        self.lyrics_file_paras = []

        for fidx, lyric_file in enumerate(self.lyric_files):
            with open(self.lyrics_path + lyric_file) as fin:
                sample = json.load(fin)
                self.lyrics_file_paras.append(len(sample['paragraphs']))


        # check whether the lyric file table exists
        result = cursor.execute('SELECT count(*) FROM sqlite_master WHERE type=\'table\' AND name=\'lyric_files\'')
        result = result.fetchall()

        if result[0][0] == 0:
            # create table
            cursor.execute('CREATE TABLE IF NOT EXISTS lyric_files (file_para_id INTEGER PRIMARY KEY, file_name text, para_id int)')

            # insert into database
            for fidx, lyric_file in enumerate(self.lyric_files):
                for para_id in range(self.lyrics_file_paras[fidx]):
                    cursor.execute('INSERT INTO lyric_files (file_name, para_id) VALUES (?, ?)', (lyric_file, para_id))


    def process_lyrics(self):
        '''
        process lyrics, turn the sentences into stemmed words,
        for future query
        '''

        for fidx, lyric_file in enumerate(self.lyric_files):
            with open(self.lyrics_path + lyric_file) as fin:
                sample = json.load(fin)
                new_sample = {}
                new_sample['title'] = sample['title']
                new_sample['paragraphs'] = []
                for pidx, paragraph in enumerate(sample['paragraphs']):
                    new_paragraph = {}
                    new_paragraph['sentences'] = []
                    sentences = paragraph['sentences']
                    for sentence in sentences:
                        words = self.word_split(sentence)
                        stemmed_words = [self.ps.stem(word) for word in words]
                        new_paragraph['sentences'].append(stemmed_words)
                    new_sample['paragraphs'].append(new_paragraph)


                with open(self.processed_lyrics_path + lyric_file, 'w+') as fout:
                    json.dump(new_sample, fout)


    def word_split(self, sentence):
        '''
        split a sentence into words,
        spliter: ' ', ',', '.'
        :return: a list of words
        '''
        words = re.split(r',| ', sentence)

        # stop words table
        words = [word for word in words if word not in self.stop_words]

        # reduce regex
        words = [re.subn(self.regex, "", word)[0] for word in words]

        # to lower case
        words = [word.lower() for word in words if word != u'']

        return words


    def gen_raw_words(self):
        '''
        generate raw words from lyric files
        '''
        words = []
        for fidx, lyric_file in enumerate(self.lyric_files):
            with open(self.lyrics_path + lyric_file) as fin:
                sample = json.load(fin)
                paragraphs = sample['paragraphs']
                for paragraph in paragraphs:
                    para_words = []
                    sentences = paragraph['sentences']
                    for sentence in sentences:
                        para_words.extend(self.word_split(sentence))
                    words.append(para_words)

        self.raw_words = words


    def gen_stemmed_words(self):
        '''
        generate stemmed words from lyric files
        '''
        self.stemmed_words = []
        for line in self.raw_words:
            self.stemmed_words.append([self.ps.stem(word) for word in line])


    def gen_raw_vocab(self):
        '''
        generate vocabulary from raw words
        '''
        vocab = set()
        for lyric_words in self.raw_words:
            for word in lyric_words:
                vocab.add(word)
        self.raw_vocab = sorted(vocab)

    def gen_stemmed_vocab(self):
        '''
        generate vocabulary from stemmed words
        '''
        vocab = set()
        for lyric_words in self.stemmed_words:
            for word in lyric_words:
                vocab.add(word)
        self.stemmed_vocab = sorted(vocab)




    def save_word_count(self, cursor):
        '''
        count words occurance and save to database
        '''
        # check whether the word_file_count table exists
        result = cursor.execute('SELECT count(*) FROM sqlite_master WHERE type=\'table\' AND name=\'word_file_count\'')
        result = result.fetchall()

        if result[0][0] == 0:
            # create table
            cursor.execute('CREATE TABLE IF NOT EXISTS word_count (word text PRIMARY KEY, count int)')
            cursor.execute('CREATE TABLE IF NOT EXISTS word_file_count (word text, file_para_id int, count int, PRIMARY KEY(word, file_para_id))')

            # map reduce count
            word_count = dict()
            word_file_count = dict()

            for pidx, paragraph in enumerate(self.stemmed_words):
                for word in paragraph:
                    if word in word_count:
                        word_count[word] += 1
                    else:
                        word_count[word] = 1

                    if (word, pidx + 1) in word_file_count:
                        word_file_count[(word, pidx + 1)] += 1
                    else:
                        word_file_count[(word, pidx + 1)] = 1

            sorted(word_count)
            sorted(word_file_count)

            for key in word_count:
                cursor.execute('INSERT INTO word_count (word, count) VALUES (?, ?)',
                               (key, word_count[key]))

            for key in word_file_count:
                cursor.execute('INSERT INTO word_file_count (word, file_para_id, count) VALUES (?, ?, ?)',
                               (key[0], key[1], word_file_count[key]))



    def save_b_gram(self, cursor):
        '''
        save the b-gram information of words into database
        '''

        # check whether the lyric file table exists
        result = cursor.execute('SELECT count(*) FROM sqlite_master WHERE type=\'table\' AND name=\'word_b_gram\'')
        result = result.fetchall()

        if result[0][0] == 0:
            # b-gram data to insert
            b_grams = []

            for word in self.raw_vocab:
                new_word = "$" + word + "$"
                for i in range(len(new_word)-1):
                    b_gram = new_word[i: i+2]
                    b_grams.append((b_gram, word))

            # create table
            cursor.execute('CREATE TABLE IF NOT EXISTS word_b_gram (b_gram text, word text, PRIMARY KEY(b_gram, word))')

            # create index
            cursor.execute('CREATE INDEX b_gram_index on word_b_gram (b_gram)')

            b_grams = list(set(b_grams))
            # insert data
            cursor.executemany('INSERT INTO word_b_gram (b_gram, word) VALUES (?, ?)', b_grams)