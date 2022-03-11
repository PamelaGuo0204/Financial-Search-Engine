from flask import Flask, render_template, request, jsonify,redirect, url_for
import Group as g
from flask_pymongo import PyMongo
import math
import pickle
from scipy import sparse
import numpy as np


#创建Flask对象app并初始化
app = Flask(__name__)

app.config['DEBUG'] = True  # 开启 debug
mongo = PyMongo(app, uri="mongodb+srv://ttds:ttdsyyds@cluster1.22kwt.mongodb.net/TTDS?retryWrites=true&w=majority")  # 连接数据库




#从数据库中查找信息
def find_data(data_dic):
    results = mongo.db.data.find(data_dic)
    return results


#从数据库中查找记录的总条数
def count_data(data_dic):
    results = mongo.db.data.count_documents(data_dic)
    return results
#分页
def get_page(total,p):
    show_page = 5   # 显示的页码数
    pageoffset = 2  # 偏移量
    start = 1    #分页条开始
    end = total  #分页条结束

    if total > show_page:
        if p > pageoffset:
            start = p - pageoffset
            if total > p + pageoffset:
                end = p + pageoffset
            else:
                end = total
        else:
            start = 1
            if total > show_page:
                end = show_page
            else:
                end = total
        if p + pageoffset > total:
            start = start - (p + pageoffset - end)
    #用于模版中循环
    dic = range(start, end + 1)
    return dic


#通过python装饰器的方法定义路由地址
@app.route("/")
#定义方法 用jinjia2引擎来渲染页面，并返回一个index.html页面
def root():
    return render_template("index.html")
#定义app在8080端口运行

#link the page
@app.route("/aboutus/")
def aboutus():
    return render_template("aboutus.html")
@app.route("/advancesearch/")
def advancesearch():
    return render_template("advancesearch.html")
@app.route("/readmore1/")
def readmore1():
    return render_template("readmore1.html")
@app.route("/readmore2/")
def readmore2():
    return render_template("readmore2.html")
@app.route("/readmore3/")
def readmore3():
    return render_template("readmore3.html")
@app.route("/readmore4/")
def readmore4():
    return render_template("readmore4.html")
@app.route("/index/")
def index():
    return render_template("index.html")



#show the result
@app.route("/result/", methods=['GET','POST'])
def show():
    p = request.args.get('p')
    show_status = 0
    if not p:
        p = 1
    else:
        p = int(p)
        if p > 1:
            show_status = 1
    limit_start = (p - 1) * 10

    if request.method == 'POST':
        global text
        text = request.form["txt"]
    # if the input is empty, stay on the same page
    if text!= "":
        global result
        result = g.output(text)
        # doc = find_data({'docno': {"$in": result}})
        doc = find_data({'docno': {"$in": result}}).limit(10).skip(limit_start)
            #总页数
        total = count_data({'docno': {"$in": result}})
        page_total = int(math.ceil(total / 10))
        page_list = get_page(page_total, p)
        datas = {
                'data_list': doc,
                'p': p,
                'page_total': page_total,
                'show_status': show_status,
                'page_list': page_list
            }
        return render_template("outcome.html", text=text,datas=datas)
    else:
        return redirect(url_for('index'))



@app.route('/result/time/',methods=['GET','POST'])
def select_time():
    p = request.args.get('p')
    show_status = 0
    if not p:
        p = 1
    else:
        p = int(p)
        if p > 1:
            show_status = 1
    limit_start = (p - 1) * 10

    if request.method == 'POST':
        global time
        global text1
        time = str(request.form["time"])
        text1 = request.form["txt"]
    if text1 != "":
        global results
        results = g.output(text1)

    if time == "Anytime":
        doc = find_data({'docno': {"$in": results}}).limit(10).skip(limit_start)
        # 总页数
        total = count_data({'docno': {"$in": results}})
        page_total = int(math.ceil(total / 10))
        page_list = get_page(page_total, p)
        datas = {
            'data_list': doc,
            'p': p,
            'page_total': page_total,
            'show_status': show_status,
            'page_list': page_list
        }
        return render_template("outcome1.html", text=text1, datas=datas)

    elif time == "Since 2013":
        doc = find_data({'docno': {"$in": results},'time':{"$gte":"2013-01-01T00:00:00Z","$lt":"2013-12-31T23:59:99Z"}}).limit(10).skip(limit_start)
        # 总页数
        total = count_data({'docno': {"$in": results},'time':{"$gte":"2013-01-01T00:00:00Z","$lt":"2013-12-31T23:59:99Z"}})
        page_total = int(math.ceil(total / 10))
        page_list = get_page(page_total, p)
        datas = {
            'data_list': doc,
            'p': p,
            'page_total': page_total,
            'show_status': show_status,
            'page_list': page_list
        }
        return render_template("outcome1.html", text=text1,datas=datas)

    elif time == "Since 2014":
        doc = find_data(
            {'docno': {"$in": results}, 'time': {"$gte": "2014-01-01T00:00:00Z", "$lt": "2014-12-31T23:59:99Z"}}).limit(
            10).skip(limit_start)
        # 总页数
        total = count_data({'docno': {"$in": results}, 'time': {"$gte": "2014-01-01T00:00:00Z", "$lt": "2014-12-31T23:59:99Z"}})
        page_total = int(math.ceil(total / 10))
        page_list = get_page(page_total, p)
        datas = {
            'data_list': doc,
            'p': p,
            'page_total': page_total,
            'show_status': show_status,
            'page_list': page_list
        }
        return render_template("outcome1.html", text=text1,datas=datas)

    elif time == "Since 2015":
        doc = find_data(
            {'docno': {"$in": results}, 'time': {"$gte": "2015-01-01T00:00:00Z", "$lt": "2015-12-31T23:59:99Z"}}).limit(
            10).skip(limit_start)
        # 总页数
        total = count_data({'docno': {"$in": results}, 'time': {"$gte": "2015-01-01T00:00:00Z", "$lt": "2015-12-31T23:59:99Z"}})
        page_total = int(math.ceil(total / 10))
        page_list = get_page(page_total, p)
        datas = {
            'data_list': doc,
            'p': p,
            'page_total': page_total,
            'show_status': show_status,
            'page_list': page_list
        }
        return render_template("outcome1.html", text=text1,datas=datas)

    elif time == "Since 2016":
        doc = find_data(
            {'docno': {"$in": results}, 'time': {"$gte": "2016-01-01T00:00:00Z", "$lt": "2016-12-31T23:59:99Z"}}).limit(
            10).skip(limit_start)
        # 总页数
        total = count_data({'docno': {"$in": results}, 'time': {"$gte": "2016-01-01T00:00:00Z", "$lt": "2016-12-31T23:59:99Z"}})
        page_total = int(math.ceil(total / 10))
        page_list = get_page(page_total, p)
        datas = {
            'data_list': doc,
            'p': p,
            'page_total': page_total,
            'show_status': show_status,
            'page_list': page_list
        }
        return render_template("outcome1.html", text=text1,datas=datas)


#advance search
@app.route("/advanced_search/",methods=['GET','POST'])
def advanced_search():
    p = request.args.get('p')
    show_status = 0
    if not p:
        p = 1
    else:
        p = int(p)
        if p > 1:
            show_status = 1
    limit_start = (p - 1) * 10

    if request.method == 'POST':
        global text
        text = request.form["txt"]
        title = request.form["type"]
    print(title)

    if title == "Title":
        global result_T
        result_T = g.outputHeadline(text)
        # doc = find_data({'docno': {"$in": result}})
        doc = find_data({'docno': {"$in": result_T}}).limit(10).skip(limit_start)
        # 总页数
        total = count_data({'docno': {"$in": result_T}})
        page_total = int(math.ceil(total / 10))
        page_list = get_page(page_total, p)
        datas = {
            'data_list': doc,
            'p': p,
            'page_total': page_total,
            'show_status': show_status,
            'page_list': page_list
        }
        return render_template("outcome.html", text=text, datas=datas)


    if title == "Article":
        global result_A
        result_A = g.outputContent(text)
        # doc = find_data({'docno': {"$in": result}})
        doc = find_data({'docno': {"$in": result_A}}).limit(10).skip(limit_start)
        # 总页数
        total = count_data({'docno': {"$in": result_A}})
        page_total = int(math.ceil(total / 10))
        page_list = get_page(page_total, p)
        datas = {
            'data_list': doc,
            'p': p,
            'page_total': page_total,
            'show_status': show_status,
            'page_list': page_list
        }
        return render_template("outcome.html", text=text, datas=datas)


    if title == "Full text":
        global result_F
        result_F = g.output(text)
        # doc = find_data({'docno': {"$in": result}})
        doc = find_data({'docno': {"$in": result_F}}).limit(10).skip(limit_start)
        # 总页数
        total = count_data({'docno': {"$in": result_F}})
        page_total = int(math.ceil(total / 10))
        page_list = get_page(page_total, p)
        datas = {
            'data_list': doc,
            'p': p,
            'page_total': page_total,
            'show_status': show_status,
            'page_list': page_list
        }
        return render_template("outcome.html", text=text, datas=datas)



if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8080,debug=False)
    # app.run(port=80, debug=True)


