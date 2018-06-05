# coding: utf-8

'''
语言学 配置
'''
# 停用词表
STOPWORDS = [u'a', u'am', u'an', u'is', u'are', u'as', u'at', u'and', u'be', u'', u'the']

# 单词切片
SPLITER = r",| |\n|\t|　"

# 单词过滤器
FILTER = "\r*\n*\t*( )*[,，\.。、~\_\-：:《》！!<>?？;；\"‘’“”/\\\[\]【】「」\{\}\(\)（）]*( )*\t*\n*"
