from flask import Flask, render_template, request, jsonify,redirect, url_for
import Group as g
from flask_pymongo import PyMongo

#创建Flask对象app并初始化
app = Flask(__name__)

app.config['DEBUG'] = True  # 开启 debug
mongo = PyMongo(app, uri="mongodb+srv://ttds:ttdsyyds@cluster0.22kwt.mongodb.net/TTDS?retryWrites=true&w=majority")  # 连接数据库


# run this once
# --------
# m=backend_model.Model()
# m.prepare_model()
# --------

#从数据库中查找信息
def find_data(data_dic):
    result = mongo.db.data.find(data_dic)
    return result

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

#get the query from the page
# @app.route("/query/", methods=['GET','POST'])
# def get_query():
#     if request.method == 'POST':
#         text = request.form["txt"]
#     # if the input is empty, stay on the same page
#         if text!= "":
#             result = g.output(text)
#             doc = find_data({'docno': {"$in": result}})
#         return doc

#show the result
@app.route("/result/", methods=['GET','POST'])
def result():
    if request.method == 'POST':
        text = request.form["txt"]
    # if the input is empty, stay on the same page
        if text!= "":
            result = g.output(text)
            doc = find_data({'docno': {"$in": result}})
            return render_template("outcome.html", results=doc)
        else:
            return redirect(url_for('index'))



app.route('/time/',methods=['GET','POST'])
def get_time():
    if request.method == 'POST':
        time = request.form["time"]
        print(time)
    return render_template("aboutus.html")


class Pagination(object):
    """
    paginate.page current page
    paginate.pages total page
    paginate.total total data
    """

    def __init__(self, page,datas=[],page_size=10):
        try:
            current_page = int(page)
        except Exception as e:
            current_page = 1
        if current_page <= 0:
            current_page = 1

        self
        ## 10 per page
        self.page_size = page_size
        # current page
        self.page = current_page
        # total data size
        self.total = len(datas)
        # total page
        _pages = (self.total + page_size - 1) / page_size
        self.pages = int(_pages)
        self.has_prev = current_page > 1 and  current_page <= self.pages if True else False
        self.has_next = current_page < self.pages if True else False
        start_index = (self.page-1)*self.page_size
        end_index = self.page*self.page_size
        self.items = datas[start_index:end_index]

    @property
    def prev_num(self):
        if self.has_prev:
            return int(self.page - 1)
        else:
            return self.pages

    @property
    def next_num(self):
        if self.has_next:
            return int(self.page + 1)
        else:
            return self.pages



    def iter_pages(self):
        for num in range(1, self.pages + 1):
                yield num


if __name__ == '__main__':
    app.run(port=8080)



