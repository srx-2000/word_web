from flask import Flask
from db.db_client import db_client
from util.Code_util import Code_util
from util.Config_loader import Config_loader
from util.logHandler import LogHandler
import time
from flask import Response, Flask, request, jsonify, send_from_directory, make_response

app = Flask(__name__)
client = db_client()
client.init_db()
loader = Config_loader()
log = LogHandler("word_web.log")
code_util = Code_util()

api_list = [
    {"url": "/upload", "method": "post", "params": "image:file", "desc": "上传一个图片【upload single image】"},
    {"url": "/show", "method": "get", "params": "/image_uuid", "desc": "在线浏览一个图片【show single image】"},
    {"url": "/all", "method": "get", "params": "", "desc": "返回所有图片的信息【show all image info】"},
    {"url": "/query", "method": "get", "params": "/year/month/day", "desc": "根据传入的年月日搜索图片【query image info by date】"},
    {"url": "/download", "method": "get", "params": "/image_uuid", "desc": "下载指定图片【download single image】"},
]


@app.route('/')
def index():
    return jsonify({"api_list": api_list})


@app.route('/add_word', methods=["post"])
def add_word():
    year = time.strftime("%Y", time.localtime())
    month = time.strftime("%m", time.localtime())
    day = time.strftime("%d", time.localtime())
    user_uuid = request.form.get("user_uuid")
    word = request.form.get("word")
    mean = request.form.get("mean")
    flag = client.insert_word(user_uuid, word, mean, year, month, day)
    if flag:
        return jsonify({"flag": True, "message": "添加成功！"})
    return jsonify({"flag": False, "message": "添加失败！"})


@app.route('/login', methods=["post"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    data = client.select_single_user_by_login(username=username, password=password)
    if data != None:
        return jsonify({"flag": True, "message": "登录成功", "user_data": data})
    return jsonify({"flag": False, "message": "登录失败", "user_data": None})


@app.route("/signup", methods=["post"])
def register():
    user_uuid = code_util.get_uuid()
    username = request.form.get("username")
    password = request.form.get("password")
    flag = client.insert_user(username, password, user_uuid)
    if flag:
        return jsonify({"flag": True, "message": "注册成功！"})
    return jsonify({"flag": False, "message": "注册失败！"})


@app.route('/query/<string:uuid>/<string:year>/<string:month>/<string:day>', methods=["get"])
@app.route('/query/<string:uuid>/<string:year>/<string:month>', methods=["get"])
@app.route('/query/<string:uuid>/<string:year>', methods=["get"])
@app.route('/query/<string:uuid>', methods=["get"])
def show_word_by_date(uuid, year=None, month=None, day=None):
    datas = client.select_word_by_date(uuid, year, month, day)
    if len(datas) == 0:
        return jsonify({"message": "no find any image info"})
    info_list = []
    for info in datas:
        info_list.append(
            {"id": info[0], "user_uid": info[1], "word": info[2], "mean": info[3], "year": info[4], "month": info[5],
             "day": info[6], "status": info[-1]})
    return jsonify({"info_list": info_list, "status": "success"})


if __name__ == '__main__':
    app.run(host=loader.get_server_host(), port=loader.get_server_port())
