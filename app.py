import re
import time
from wsgiref.simple_server import make_server

from flask import Flask, request, jsonify
from flask_cors import *

from db.db_client import db_client
from translate_api import spider
from util.Code_util import Code_util
from util.Config_loader import Config_loader
from util.logHandler import LogHandler

app = Flask(__name__)
client = db_client()
client.init_db()
loader = Config_loader()
log = LogHandler("word_web")
code_util = Code_util()

api_list = [
    {"/show_spider_result": {"message": "获取爬虫（使用金山词霸、百度翻译接口获取中文含义以及词根）结果", "method": "get"}},
    {"/show_word_by_date": {"message": "通过单词添加日期批量查询单词", "method": "get"}},
    {"/is_username_exist": {"message": "用于做用户验证", "method": "get"}},
    {"/high_frequency": {"message": "获取高频词汇", "method": "get"}},
    {"/search_word": {"message": "单词中英文检索", "method": "get"}},
    {"/batch_delete_word": {"message": "批量删除单词", "method": "post"}},
    {"/batch_add_word": {"message": "批量添加单词", "method": "post"}},
    {"/update_word": {"message": "更新单词属性", "method": "post"}},
    {"/add_word": {"message": "添加单个单词", "method": "post"}},
    {"/register": {"message": "用户注册", "method": "post"}},
    {"/login": {"message": "用户登录", "method": "post"}},
]

CORS(app, supports_credentials=True)


@app.route('/')
def index():
    return jsonify({"后端接口说明：": api_list})


@app.before_request
def before_request():
    if request.method == 'GET':
        data = request.args
    else:
        data = request.form.items()
        data = [v for k, v in data]
    if data:
        pattern = r"\b(and|like|exec|insert|select|drop|grant|alter|delete|update|count|chr|mid|master|truncate|char|delclare|or)\b|(*|;)"
        for v in data:
            v = str(v).lower()
            r = re.search(pattern, v)
            if r:
                log.warning(f"有大佬对我下手了，注意呀,大佬Ip地址是：{request.remote_addr}")
                return "大佬还请手下留情，该网站仅用于私人学习用途"


@app.route("/get_spider_result/<string:word>", methods=["get"])
def show_spider_result(word):
    mean_result = spider.get_mean(word)
    if mean_result["flag"]:
        affix = spider.get_affix(word)
        return {"mean": mean_result["mean"], "affix": affix}
    else:
        return {"mean": mean_result["mean"], "affix": None}


@app.route('/update_word', methods=["post"])
def update_word():
    data = request.get_json()
    user_uuid = data["user_uid"]
    word_id = data["id"]
    word = data["word"]
    mean = data["mean"]
    memory_way = data["memory_way"]
    flag = client.update_word(word_id, user_uuid, word, mean, memory_way)
    if flag >= 1:
        return jsonify({"flag": True, "message": "修改成功！"})
    return jsonify({"flag": False, "message": "修改失败！"})


@app.route('/add_word', methods=["post"])
def add_word():
    year = time.strftime("%Y", time.localtime())
    month = time.strftime("%m", time.localtime())
    day = time.strftime("%d", time.localtime())
    data = request.get_json()
    user_uuid = data["user_uuid"]
    word = data["word"]
    mean = data["mean"]
    memory_way = data["memory_way"]
    flag = client.insert_word(user_uuid, word, mean, memory_way, year, month, day)
    if flag:
        return jsonify({"flag": True, "message": "添加成功！"})
    return jsonify({"flag": False, "message": "添加失败！"})


@app.route("/batch_add_word", methods=['post'])
def batch_add_word():
    year = time.strftime("%Y", time.localtime())
    month = time.strftime("%m", time.localtime())
    day = time.strftime("%d", time.localtime())
    data = request.get_json()
    # print(data)
    user_uuid = data["user_uuid"]
    word_list = data["wordList"]
    mean_list = data["meanList"]
    memory_way_list = data["memory_wayList"]
    count = 0
    for i in range(0, len(word_list)):
        flag = client.insert_word(user_uuid, word_list[i], mean_list[i], memory_way_list[i], year, month, day)
        if flag:
            count += 1
    if count == len(word_list):
        return jsonify({"flag": True, "message": "添加成功！"})
    return jsonify({"flag": False, "message": "有部分单词添加失败，请自己核实！"})


@app.route("/batch_delete_word", methods=['post'])
def batch_delete_word():
    data = request.get_json()
    user_uuid = data["user_uuid"]
    word_list = data["word_list"]
    count = 0
    for i in word_list:
        year = i["year"]
        month = i["month"]
        day = i["day"]
        mean = i["mean"]
        word = i["word"]
        word_id = i["id"]
        memory_way = i["memory_way"]
        flag = client.delete_single_word(word_id, word, mean, memory_way, user_uuid, year, month, day)
        if flag:
            count += 1
    if count == len(word_list):
        return jsonify({"flag": True, "message": "删除成功！"})
    else:
        return jsonify({"flag": False, "message": "有部分单词删除失败，请自己核实！"})


@app.route('/login', methods=["post"])
def login():
    data = request.get_json()
    username = data["username"]
    password = data["password"]
    log.info(f'用户：{username}登录,密码是:{password}')
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


@app.route('/high_frequency/<string:uuid>', methods=["get"])
def high_frequency(uuid):
    datas = client.get_high_frequency(uuid)
    info_list = []
    if len(datas) == 0:
        return jsonify({"word_list": info_list, "message": "未查到任何单词", "word_count": len(datas)})
    for info in datas:
        info_list.append(
            {"user_uid": uuid, "word": info[0], "mean": info[1], "memory_way": info[2], "frequency": info[-1]})
    return jsonify({"word_list": info_list, "message": "查询成功", "word_count": len(datas)})


@app.route('/search/<string:uuid>/<string:word_prefix>/<int:prefix_type>/<int:status>', methods=["get"])
@app.route('/search/<string:uuid>/<int:prefix_type>/<int:status>', methods=["get"])
def search_word(uuid, word_prefix="", prefix_type=1, status=1):
    datas = client.search_word(uuid, word_prefix, prefix_type, status)
    info_list = []
    if len(datas) == 0:
        return jsonify({"word_list": info_list, "message": "未查到任何单词", "word_count": len(datas)})
    for info in datas:
        info_list.append(
            {"id": info[0], "user_uid": info[1], "word": info[2], "mean": info[3], "memory_way": info[4],
             "year": info[5], "month": info[6],
             "day": info[7], "status": info[-1]})
    return jsonify({"word_list": info_list, "message": "查询成功", "word_count": len(datas)})


@app.route('/query/<string:uuid>/<int:page>/<int:page_size>/<string:year>/<string:month>/<string:day>/<int:status>',
           methods=["get"])
@app.route('/query/<string:uuid>/<int:page>/<int:page_size>/<string:year>/<string:month>/<int:status>', methods=["get"])
@app.route('/query/<string:uuid>/<int:page>/<int:page_size>/<string:year>/<int:status>', methods=["get"])
@app.route('/query/<string:uuid>/<int:page>/<int:page_size>/<int:status>', methods=["get"])
@app.route('/query/<string:uuid>/<int:page>/<int:status>', methods=["get"])
def show_word_by_date(uuid, page_size=None, page=None, year=None, month=None, day=None, status=1):
    if page == None:
        return jsonify({"message": "查询方式有误，请检查"})
    if page_size == None:
        page_size = 30
    elif page > 0:
        page = page - 1
    else:
        page = 0
    datas = client.select_word_by_date(uuid, page, page_size, year, month, day, status)
    word_count = client.query_count(uuid, year, month, day, status)
    info_list = []
    if len(datas) == 0:
        return jsonify({"word_list": info_list, "message": "未查到任何单词", "word_count": word_count[0]})
    for info in datas:
        info_list.append(
            {"id": info[0], "user_uid": info[1], "word": info[2], "mean": info[3], "memory_way": info[4],
             "year": info[5], "month": info[6],
             "day": info[7], "status": info[-1]})
    return jsonify({"word_list": info_list, "message": "查询成功", "word_count": word_count[0]})


@app.route("/isUsernameExist/<string:username>", methods=["get"])
def is_username_exist(username):
    flag = client.is_username_exist(username)
    return jsonify({"flag": flag})


if __name__ == '__main__':
    srv = make_server(loader.get_server_host(), int(loader.get_server_port()), app)
    srv.serve_forever()
    # app.run(host=loader.get_server_host(), port=loader.get_server_port())
