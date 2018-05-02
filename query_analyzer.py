
import re
import datetime
from nltk.stem import PorterStemmer

class QueryAnalyzer(object):
    '''
    query analyzer module analyze an input query,
    and translate it into set operations,
    finally return the query results
    '''

    def __init__(self):
        self.ps = PorterStemmer()


    def analyze(self, query_str, conn):
        '''
        analyze the query string and
        return the lyric file index list
        that satisfy the query
        '''
        # start clock
        self.start_time = datetime.datetime.now()

        # split string to tokens and turn it to postfix
        postfix_tokens = self.split_tokens(query_str)

        lyrics_file_idxs = self.query_computation(postfix_tokens, conn)

        # display results
        self.display_query_results(lyrics_file_idxs, conn)




    def split_tokens(self, query_str):
        '''
        split the query string into tokens,
        return the postfix tokens
        '''

        query_tokens = []

        # split with spaces
        tmp_tokens = re.split(r' +', query_str)

        tmp_tokens = [tmp_token for tmp_token in tmp_tokens if tmp_token != '']

        # split '(' and ')'
        for tmp_token in tmp_tokens:
            if tmp_token[0] == '(':
                query_tokens.append('(')
                query_tokens.append(tmp_token[1:])
            elif tmp_token[-1] == ')':
                query_tokens.append(tmp_token[:-1])
                query_tokens.append(')')
            else:
                query_tokens.append(tmp_token)

        # filter empty str
        query_tokens = [token for token in query_tokens if token != '']

        return self.infix_to_postfix(query_tokens)


    def infix_to_postfix(self, infix_tokens):
        '''
        transform infix tokens to postfix tokens
        '''
        postfix_tokens = []
        stack = []

        for token in infix_tokens:
            if token is '(':
                stack.append('(')
            elif token is ')':
                # pop stack elements, until '(' is met
                while len(stack) is not 0 and stack[-1] is not '(':
                    postfix_tokens.append(stack[-1])
                    stack.pop()
                assert len(stack) > 0, 'missing ( in query'
                stack.pop()
            elif token == 'AND' or token == 'OR' or token == 'NOT':
                # priority check
                while len(stack) != 0 and self.priority(stack[-1]) >= self.priority(token):
                    postfix_tokens.append(stack[-1])
                    stack.pop()
                stack.append(token)

            else: # query words
                postfix_tokens.append(token)

        while len(stack) is not 0:
            postfix_tokens.append(stack[-1])
            stack.pop()

        return postfix_tokens


    def query_computation(self, query_tokens, conn):
        '''
        compute the result of query expression
        with set theory, each query word represents
        the indexes of lyric files that includes it.
        :return: the final result of file indexes
        '''

        cursor = conn.execute('SELECT file_id FROM word_file_count')
        R = [row[0] for row in cursor]
        R = list(set(R))

        operators = ['AND', 'OR', 'NOT']
        operands = []

        for token in query_tokens:
            # if is operand
            if token not in operators:
                operands.append(self.get_file_idxs(token, conn))
            else: # is operator
                if token == 'AND':
                    assert len(operands) >= 2, 'query expression error!'
                    result = self.AND(operands[-1], operands[-2])
                    del operands[-2:]
                    operands.append(result)
                elif token == 'OR':
                    assert len(operands) >= 2, 'query expression error!'
                    result = self.OR(operands[-1], operands[-2])
                    del operands[-2:]
                    operands.append(result)
                elif token == 'NOT':
                    assert len(operands) >= 1, 'query expression error!'
                    operands[-1] = self.NOT(R, operands[-1])

        assert len(operands) > 0, 'query expression error!'

        return operands[0]


    def get_file_idxs(self, word, conn):
        '''
        given a word, return the indexes of
        lyrics files that contain the word
        '''

        # stemming the query word
        word = self.ps.stem(word)

        result = []

        cursor = conn.execute('SELECT file_id, count FROM word_file_count WHERE word=?', [word])

        for row in cursor:
            result.append(row[0])

        return result

    def display_query_results(self, file_idxs, conn):
        '''
        display the results of query
        '''

        cursor = conn.execute('SELECT file_name FROM lyric_files WHERE file_id IN (%s)'
                              % ("?," * len(file_idxs))[:-1], file_idxs)

        self.end_time = datetime.datetime.now()
        query_time = (self.end_time - self.start_time).microseconds

        print len(file_idxs), 'results found. (in', query_time, 'ms)'

        for row in cursor:
            print(row[0])


    def priority(self, operator):
        '''
        return the priority of operators,
        now supports 'AND' 'OR' 'NOT',
        2: NOT
        1: AND OR
        '''
        if operator == 'AND' or operator == 'OR':
            return 1
        elif operator == 'NOT':
            return 2


    def AND(self, A, B):
        '''
        set intersection
        '''
        assert isinstance(A, list), 'invalid type of A, should be <class list>'
        assert isinstance(B, list), 'invalid type of B, should be <class list>'

        A_len = len(A)
        B_len = len(B)
        A_locate = 0
        B_locate = 0
        result = []

        while A_locate < A_len and B_locate < B_len:
            doc_a = A[A_locate]
            doc_b = B[B_locate]

            if doc_a == doc_b:
                result.append(doc_a)
                B_locate = B_locate + 1
                A_locate = A_locate + 1
            elif doc_a > doc_b:
                B_locate = B_locate + 1
            else:
                A_locate = A_locate + 1

        return result


    def OR(self, A, B):
        '''
        set union
        '''
        assert isinstance(A, list), 'invalid type of A, should be <class list>'
        assert isinstance(B, list), 'invalid type of B, should be <class list>'

        A_len = len(A)
        B_len = len(B)
        A_locate = 0
        B_locate = 0
        result = []

        while A_locate < A_len and B_locate < B_len:
            doc_a = A[A_locate]
            doc_b = B[B_locate]

            if doc_a == doc_b:
                result.append(doc_a)
                B_locate = B_locate + 1
                A_locate = A_locate + 1
            elif doc_a > doc_b:
                result.append(doc_b)
                B_locate = B_locate + 1
            else:
                result.append(doc_a)
                A_locate = A_locate + 1
        return result + ((B[B_locate:B_len]) if (A_locate == A_len) else (A[A_locate:A_len]))


    def NOT(self, docs_A, docs_B):
        '''
        set NOT A
        '''
        assert isinstance(docs_A, list), 'invalid type of A, should be <class list>'
        assert isinstance(docs_B, list), 'invalid type of B, should be <class list>'

        A_len = len(docs_A)
        B_len = len(docs_B)
        A_locate = 0
        B_locate = 0
        result = []
        while A_locate < A_len and B_locate < B_len:
            doc_a = docs_A[A_locate]
            doc_b = docs_B[B_locate]
            if doc_a == doc_b:
                B_locate = B_locate + 1
                A_locate = A_locate + 1
            elif doc_a > doc_b:
                B_locate = B_locate + 1
            else:
                result.append(doc_a)
                A_locate = A_locate + 1
        return result + ([] if (A_locate == A_len) else  (docs_A[A_locate:A_len]))