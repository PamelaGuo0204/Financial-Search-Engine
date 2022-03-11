from flask import Flask,render_template,request
from flask_pymongo import PyMongo
app = Flask(__name__)

app.config['DEBUG'] = True  # 开启 debug
mongo = PyMongo(app, uri="mongodb+srv://ttds:ttdsyyds@cluster0.22kwt.mongodb.net/TTDS?retryWrites=true&w=majority")  # 连接数据库

def add_data_to_mongo(data_dic):
    """
            单字段修改数据
            collection_name: 表名字符串
            data_dic: 数据字典
        """
    mongo.db.testdata.insert(data_dic)
    # mycol = mongo.db[collection_name]
    # mycol.insert(data_dic)
#从数据库中查找信息
def find_data(data_dic):
    result = mongo.db.data.find(data_dic)
    return result

#按照时间查找数据:
# def find_data_by_year()
#link the page
@app.route("/aboutus/")
def aboutus():
    return render_template("aboutus.html")
@app.route("/advancesearch/")
def advancesearch():
    return render_template("advancesearch.html")
@app.route("/index/")
def index():
    return render_template("index.html")

@app.route('/time/',methods=['GET','POST'])
def get_time():
    if request.method == 'POST':
        time = request.form["time"]
        print(time)
    return render_template("aboutus.html");

# @app.route('/')
# def hello_world():
#     results = []
#     #循环语句，循环查找信息，有误
#     for i in range(437306,437316):
#         results.append(str(i))
#     result = find_data({'docno': {"$in": results}})
#     print(results)
#     if results:
#         #在网页显示信息
#         return render_template("outcome.html",results=result)

@app.route('/',methods=['GET','POST'])
def select_time_2013():
    results = []
    # 循环语句，循环查找信息，有误
    for i in range(437306, 437316):
        results.append(str(i))
        # {'docno': {"$in": results},
    result = find_data({'docno': {"$in": results},'time':{"$gte":"2013-10-22T09:50:00Z","$lt":"2013-10-23T10:34:14Z"}})
    if results:
        #在网页显示信息
        return render_template("outcome.html",results=result)

if __name__ == '__main__':
    app.run()
