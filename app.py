from flask import Response, Flask, request, jsonify, send_from_directory, make_response
from db.db_client import db_client
from util.Code_util import Code_util
from util.Config_loader import Config_loader
from util.logHandler import LogHandler
import time
from flask_cors import *
import json

app = Flask(__name__)
client = db_client()
client.init_db()
loader = Config_loader()
log = LogHandler("word_web.log")
code_util = Code_util()

api_list = [
    # {"url": "/upload", "method": "post", "params": "image:file", "desc": "上传一个图片【upload single image】"},
    # {"url": "/show", "method": "get", "params": "/image_uuid", "desc": "在线浏览一个图片【show single image】"},
    # {"url": "/all", "method": "get", "params": "", "desc": "返回所有图片的信息【show all image info】"},
    # {"url": "/query", "method": "get", "params": "/year/month/day", "desc": "根据传入的年月日搜索图片【query image info by date】"},
    # {"url": "/download", "method": "get", "params": "/image_uuid", "desc": "下载指定图片【download single image】"},
]

CORS(app, supports_credentials=True)


@app.route('/')
def index():
    return jsonify({"api_list": api_list})


@app.route('/add_word', methods=["post"])
def add_word():
    year = time.strftime("%Y", time.localtime())
    month = time.strftime("%m", time.localtime())
    day = time.strftime("%d", time.localtime())
    data = request.get_json()
    user_uuid = data["user_uuid"]
    word = data["word"]
    mean = data["mean"]
    flag = client.insert_word(user_uuid, word, mean, year, month, day)
    if flag:
        return jsonify({"flag": True, "message": "添加成功！"})
    return jsonify({"flag": False, "message": "添加失败！"})


@app.route("/batch_add_word", methods=['post'])
def batch_add_word():
    year = time.strftime("%Y", time.localtime())
    month = time.strftime("%m", time.localtime())
    day = time.strftime("%d", time.localtime())
    data = request.get_json()
    user_uuid = data["user_uuid"]
    word_list = data["wordList"]
    mean_list = data["meanList"]
    count = 0
    for i in range(0, len(word_list)):
        flag = client.insert_word(user_uuid, word_list[i], mean_list[i], year, month, day)
        if flag:
            count += 1
    if count == len(word_list):
        return jsonify({"flag": True, "message": "添加成功！"})
    return jsonify({"flag": False, "message": "有部分单词添加失败，请自己核实！"})


@app.route('/login', methods=["post"])
def login():
    data = request.get_json()
    username = data["username"]
    password = data["password"]
    print(username)
    print(password)
    # print(request.form)
    for i in request.form:
        print(request.form[i])
    data = client.select_single_user_by_login(username=username, password=password)
    if data != None:
        return jsonify({"flag": True, "message": "登录成功", "user_data": data})
    return jsonify({"flag": False, "message": "登录失败", "user_data": None})


@app.route("/signup", methods=["post"])
def register():
    user_uuid = code_util.get_uuid()
    data = request.get_json()
    username = data["username"]
    password = data["password"]
    flag = client.insert_user(username, password, user_uuid)
    if flag:
        return jsonify({"flag": True, "message": "注册成功！"})
    return jsonify({"flag": False, "message": "注册失败！"})


@app.route('/query/<string:uuid>/<int:page>/<int:page_size>/<string:year>/<string:month>/<string:day>', methods=["get"])
@app.route('/query/<string:uuid>/<int:page>/<int:page_size>/<string:year>/<string:month>', methods=["get"])
@app.route('/query/<string:uuid>/<int:page>/<int:page_size>/<string:year>', methods=["get"])
@app.route('/query/<string:uuid>/<int:page>/<int:page_size>', methods=["get"])
@app.route('/query/<string:uuid>/<int:page>', methods=["get"])
def show_word_by_date(uuid, page_size=None, page=None, year=None, month=None, day=None):
    if page == None:
        return jsonify({"message": "查询方式有误，请检查"})
    if page_size == None:
        page_size = 30
    elif page > 0:
        page = page - 1
    else:
        page = 0
    datas = client.select_word_by_date(uuid, page, page_size, year, month, day)
    word_count = client.query_count(uuid, year, month, day)
    info_list = []
    if len(datas) == 0:
        return jsonify({"word_list": info_list, "message": "未查到任何单词", "word_count": word_count[0]})
    for info in datas:
        info_list.append(
            {"id": info[0], "user_uid": info[1], "word": info[2], "mean": info[3], "year": info[4], "month": info[5],
             "day": info[6], "status": info[-1]})
    return jsonify({"word_list": info_list, "message": "查询成功", "word_count": word_count[0]})


@app.route("/isUsernameExist/<string:username>", methods=["get"])
def is_username_exist(username):
    flag = client.is_username_exist(username)
    return jsonify({"flag": flag})


if __name__ == '__main__':
    app.run(host=loader.get_server_host(), port=loader.get_server_port())
