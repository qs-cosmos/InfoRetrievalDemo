# coding: utf-8
from flask import Flask
from flask import render_template
from flask import request
import re,time 
from query.query import LanguageModel

app = Flask(__name__)

model = LanguageModel()
lyrics_json = model.reader.lyrics
@app.route('/search', methods=['GET', 'POST'])
@app.route('/search/<records>/<query>/<amount>/<page>/<last_page>/<pages>', methods=['GET', 'POST'])
def search(records=None, query=None, amount=None,
           page=None, last_page=None, pages=None):
    page_size = 12
    page_amount = 8
    last_page = False
    query = request.args.get('query')
    page = request.args.get('page')
    if page is None:
        page = 1
    else:
        page = int(page)
    
    records = model.query(query)
    
    # 查询结果总数
    amount = len(records)

    # 分页
    max_page = (amount / page_size) if (amount % page_size == 0) else (amount / page_size + 1)
    if max_page > page:
        start = (page - 1) * page_size
        end = page * page_size
    else:
        start = (max_page - 1) * page_size
        end = amount
        last_page = True
    temp = records[start:end]
    
    model.database.handler()
    records = []
    for record in temp:
        docId = record[0]
        lyric = model.database.lyric(docId)
        lyric_json = lyrics_json[docId]
        content = lyric_json["content"]

        records = records + [(lyric_json["title"], lyric[1], content)]

    model.database.commit()

    start_page = 0
    end_page = 0
    # 选择页数
    if page > (page_amount / 2) and (max_page - page) > page_amount/2:
        start_page = page - page_amount / 2
        end_page = page + page_amount / 2
    elif max_page > page_amount  and (max_page - page) < page_amount/2:
        start_page = max_page - page_amount
        end_page = max_page + 1
    elif page <= (page_amount / 2) and max_page > page_amount:
        start_page = 1
        end_page = 9
    elif page <= (page_amount / 2) and max_page < page_amount:
        start_page = 1
        end_page = max_page + 1

    pages = range(start_page, end_page)

    return render_template("search_result.html", query = query, records = records,
                           amount=amount,page=page, last_page=last_page, pages=pages)

@app.route('/')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run()

