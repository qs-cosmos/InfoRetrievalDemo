import sqlite3

class Database(object):
    '''
    class database
    '''
    def __init__(self):
        self.db_name = "data/database/data.db"

    def create(self):
        '''
        create database
        '''
        self.conn = sqlite3.connect(self.db_name, isolation_level=None, timeout=100.0)
        self.conn.close()

    def handler(self):
        '''
        return the handler of database
        '''
        self.conn = sqlite3.connect(self.db_name, isolation_level=None, timeout=100.0)
        cursor = self.conn.cursor()
        return self.conn, cursor