import argparse
import logging
from database import Database
from dictionary import Dictionary
from query_analyzer import QueryAnalyzer

def parse_args():
    '''
    parse command line arguments.
    '''

    parser = argparse.ArgumentParser('Information Retrieval Demo')
    parser.add_argument('--prepare', action='store_true',
                        help='create database, prepare words from lyric files')
    parser.add_argument('--query', action='store_true',
                        help='query words combination')

    return parser.parse_args()


def prepare(args):
    logger = logging.getLogger('IR')

    # create database
    logger.info('Creating database...')
    db = Database()
    db.create()

    # get database handler
    conn, cursor = db.handler()

    # create dictionary
    logger.info('Creating dictionary')
    dic = Dictionary()

    # save file index
    dic.save_file_idx(cursor)

    # process lyrics
    #dic.process_lyrics()

    # genetate words
    dic.gen_raw_words()
    dic.gen_stemmed_words()

    # generate vocab
    dic.gen_raw_vocab()
    dic.gen_stemmed_vocab()

    # save word b-gram
    dic.save_b_gram(cursor)

    # save word count
    dic.save_word_count(cursor)

    # commit updates and close connection
    conn.commit()
    conn.close()

    logger.info('Preparation complete...')

def query(args):
    db = Database()
    conn, cursor = db.handler()

    analyzer = QueryAnalyzer(cursor)
    while True:
        query_str = raw_input("Query>> ")
        if query_str == 'exit':
            print("Bye~")
            break
        else:
            analyzer.analyze(query_str)

    conn.commit()
    conn.close()


def run():
    args = parse_args()

    logger = logging.getLogger("IR")
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if args.prepare:
        prepare(args)
    if args.query:
        query(args)

if __name__ == '__main__':
    run()