# -*- coding: utf-8 -*-
from calendar import c
from dataclasses import dataclass
import datetime
from fileinput import filename
import io
from logging import log
import logging
import os
import time
from urllib import response
import oss2
from re import A
from traceback import print_tb
import uuid
from webbrowser import get
from flask import Flask, jsonify, render_template, request, send_file, url_for, redirect, flash

from flask_httpauth import HTTPBasicAuth
from flask_cors import CORS
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy import JSON, TEXT, Text, and_, or_
from flask_apscheduler import APScheduler
# app.config['UPLOAD_FOLDER'] = r"E:/FLASK/static"
import requests
import json # 用于处理json格式数据的模块
from flask_sqlalchemy import SQLAlchemy
from flask_paginate import Pagination, get_page_parameter
from sqlalchemy.sql import text
from concurrent.futures import ThreadPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler
executor = ThreadPoolExecutor(max_workers=5)
from my_oss import OssfileUrl
from upload import UPLOAD_FILE
from zhiboba import Zhiboba
from models import *

HOST = '47.92.93.77'
PORT = '3306'
DATABASE = 'test'
USERNAME = 'root'
PASSWORD = 'aA171207'

DB_URI = "mysql+pymysql://{username}:{password}@{host}:{port}/{db}?charset=utf8&autocommit=true".format(username=USERNAME,password=PASSWORD, host=HOST,port=PORT, db=DATABASE)

app = Flask(__name__)

CORS(app)
basedir = os.path.abspath(os.path.dirname(__file__))
auth = HTTPBasicAuth()
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
BASEDIR = basedir
CSRF_ENABLED = True
SECRET_KEY = 'jklklsadhfjkhwbii9/sdf\sdf'


def auto_rollback(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as err:
            db.session.rollback()
            logging.info(err)
            raise err

    return wrapper
'''
class Config(object):  # 创建配置，用类
    # 任务列表
    JOBS = [  
        # {  # 第一个任务
        #     'id': 'job1',
        #     'func': '__main__:job_1',
        #     'args': (1, 2),
        #     'trigger': 'cron', # cron表示定时任务
        #     'hour': 19,
        #     'minute': 27
        # },
        {  # 第二个任务，每隔5S执行一次
            'id': 'job2',
            'func': '__main__:check_insert_data', # 方法名
            # 'args': (1,2), # 入参
            'trigger': 'interval', # interval表示循环任务
            'seconds': 120,
        }
    ]
'''
# scheduler=APScheduler()

scheduler = BackgroundScheduler()


class User(db.Model):  # 表名将会是 user（自动生成，小写处理）

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password = db.Column(db.String(128))

class Movie(db.Model):  # 表名将会是 movie
    id = db.Column(db.Integer, primary_key=True)  # 主键
    cover_url = db.Column(db.String(200)) 
    title = db.Column(db.String(60))  # 电影标题
    release_date = db.Column(db.String(4))  # 电影年份
    score = db.Column(db.String(4))
    actors = db.Column(db.String(500))
    def to_json(self):
        return {
                'id': self.id,
                'cover_url': self.cover_url,
                'title': self.title,
                'release_date': self.release_date,
                'score': self.score,
                'actors' : self.actors
                }


@app.route("/")
def login():
    return "hello flask"

def movie_info(start,limit):
    url = 'https://movie.douban.com/j/chart/top_list' # 数据目标地址
    params = { # 需要携带的动态参数
        'type': '2',
        'interval_id': '100:90',
        'action':'' ,
        'start':start,
        'limit':limit
        }
    '''
    模拟浏览器的身份验证信息，防止反爬
    '''
    proxies={'http':'http://127.0.0.1:10810'}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4750.0 Safari/537.36'}
    response = requests.get(url=url, params=params, headers=headers)#proxies=proxies
    data =  json.loads(response.text)
    print(data)
    #返回data和cover——url地址
    cover_urls = []
    n = len(data)
    for i in range(n):
        cover_urls.append(data[i]["cover_url"])
    return data,cover_urls

# 储存的路径
# filePath="/house/2020-10-29/xxxx.jpg"  # xxxxx  wei
# # 指定Bucket实例，所有文件相关的方法都需要通过Bucket实例来调用。
# bucket=oss2.Bucket(oss2.Auth(access_key_id, access_key_secret), endpoint, bucket_name)






@app.route('/movieList', methods=['GET', 'POST'])
# def get_mv():
#     task1 = executor.submit(movie_list)
#     task1.result()
#     return jsonify(task1.result())
def movie_list():
    db.session.remove()
    db.engine.dispose() 
    res =  db.session.query(Movie).all()[::-1]#倒序[::-1]
    
    total = db.session.query(Movie).count()
    currentPage = int(request.args.get("currentPage"))
    pageSize = int(request.args.get("pageSize"))
    start_data = (currentPage-1)*pageSize
    end_data = currentPage*pageSize
    temp=[]
    for x in res:
        temp.append(x.to_json())
    temp = temp[start_data:end_data] 
    response = {
        "code":200,
        "data":temp,
        "total":total,
        "totalPages":total % 10,
        "msg":"执行成功"
    }

    return jsonify(response)



@app.route('/searchMovie', methods=['GET', 'POST'])
def searchMovie():
    db.session.remove()
    db.engine.dispose()    
    
    title = request.args.get("movieTitle")
    actor = request.args.get("movieTitle")
    rule = or_(Movie.title.like(f'%{title}%'),Movie.actors.like(f'%{actor}%'))
    res =  db.session.query(Movie).filter(rule).all()[::-1]
    total =  db.session.query(Movie).filter(rule).count()
    currentPage = int(request.args.get("currentPage"))
    pageSize = int(request.args.get("pageSize"))
    start_data = (currentPage-1)*pageSize
    end_data = currentPage*pageSize
    temp=[]

    # movieTitle = request.args.get("movieTitle")
    # movieTitle = request.args.get("movieTitle")
    # rule = or_('%{movieTitle}%','%{actor}%')
    # res =  db.session.query(Movie).filter(rule).all()
    # total =  db.session.query(Movie).filter(Movie.title.like(f'%{movieTitle}%')).count()
    # currentPage = int(request.args.get("currentPage"))
    # pageSize = int(request.args.get("pageSize"))
    # start_data = (currentPage-1)*pageSize
    # end_data = currentPage*pageSize
    # temp=[]
    for x in res:
        temp.append(x.to_json())
        
    temp = temp[start_data:end_data]
    response = {
        "code":200,
        "data":temp,
        "total":total,
        "totalPages":total % 10,
        "msg":"执行成功"
    }
    return jsonify(response)


@app.route('/uploadFile', methods=['POST'])
def upload_file():
    db.session.remove()
    db.engine.dispose()    
    file_obj = request.files.get("file") # Flask中获取文件
    if file_obj is None:
        # 表示没有发送文件
        return "未上传文件"
    #保存文件在本地
    time_now = time.strftime("%Y%m%d%H%M%S", time.localtime())
    file_name = time_now+"_"+file_obj.filename
    file_path = os.path.join("E:/FLASK/static", file_name)
    file_obj.save(file_path)

    upload_class = UPLOAD_FILE(subfilename="image/example")#初始化oss,创建mypic/exam目录
    upload_class.upload_file(path="./static/"+file_name)
    oss = OssfileUrl()
    oss_url = oss.get_oss_lastest_pic()
    time.sleep(1)
    os.remove(file_path)

    print(file_obj)
    # print(file_path)
    return jsonify(oss_url)

@app.route('/addMovie', methods=['POST'])
def add_movie():
    db.session.remove()
    db.engine.dispose()   
    print(request.json)
    data = request.json
    title =  data["title"]
    cover_url =  data["cover_url"]
    release_date =  data["release_date"]
    actors =  data["actors"]
    score =  data["score"]
    m1 = Movie(cover_url=cover_url,title=title,release_date= release_date,score=score,actors=actors)  # 再创建一个 Movie 记录
    db.session.add(m1)
    db.session.commit()
    response = {
        "code":200,
        "msg":"执行成功"
    }
    return jsonify(response)
    
@app.route('/updateMovieInfo', methods=['POST'])
def update_movie_info():
    db.session.remove()
    db.engine.dispose()   
    print(request.json)
    data = request.json
    id = data['id']
    print("id="+str(id))
    
    title =  data["title"]
    cover_url =  data["cover_url"]
    release_date =  data["release_date"]
    actors =  data["actors"]
    score =  data["score"]
    movie = db.session.query(Movie).filter(Movie.id == id).first()
    movie.title = title
    movie.cover_url = cover_url
    movie.release_date = release_date
    movie.actors = actors
    movie.score = score
    response = {
        "code":200,
        "msg":"执行成功"
    }
    db.session.commit()
    return jsonify(response)


@app.route('/getMsg', methods=['GET', 'POST'])
def home():
    response = {
        'msg': 'Hello, Python !',
        "code":200,
        "data":{"a":1,"b":2}
    }
    return jsonify(response)

@app.route('/test', methods=['GET'])
def test():
    return json.dumps('hello world!')


@app.route('/movie', methods=['GET', 'POST'])
def get_movieinfo():
    response = {
        'msg': '末代皇帝',
        "code":200,
        "data":{"a":1,"b":2}
    }
    return jsonify(response)

#删除电影
@app.route('/delMovie', methods=['GET', 'POST'])
def del_movie():
    
    js = request.get_json()
    print("js="+str(js))
    id = js["id"]
    result = db.session.query(Movie).filter(Movie.id == id).first()
    db.session.delete(result)
    db.session.commit()
    response = {
        "code":200,
        "msg":"执行成功"
    }
    return jsonify(response)

#修改电影
@app.route('/moifyMovie', methods=['GET', 'POST'])
def moifyMovie():
    
    js = request.get_json()
    print("js="+str(js))
    id = js["id"]
    result = db.session.query(Movie).filter(Movie.id == id).first()
    db.session.delete(result)
    db.session.commit()
    response = {
        "code":200,
        "msg":"执行成功"
    }
    return jsonify(response)


def get_file_List(file_path):
    dir_List = os.listdir(file_path)
    if not dir_List:
        return
    else:
        # 注意，这里使用lambda表达式，将文件按照最后修改时间顺序升序排列
        # os.path.getmtime() 函数是获取文件最后修改时间
        # os.path.getctime() 函数是获取文件最后创建时间
        dir_List = sorted(dir_List,key=lambda x: os.path.getctime(os.path.join(file_path, x)))
        # print(dir_List)
        return dir_List

#查询数据并插入数据库修改url字段
# @auto_rollback
def check_insert_data():
    db.session.remove()
    db.engine.dispose() 
    zhibo = Zhiboba()
    res = zhibo.dianjing_list()[::-1]
    lis_way=[]
    n = len(res)
    print(n)
    for i in range(n):
        lis_way.append(res[i]["way"])
        # print("hahaha")
        # print(res[i]["id"])
        rr = res[i]["id"]
        # rule = or_(Dianjing.news_id.like(f'%{rr}%'))

        id =  db.session.query(Dianjing).filter(Dianjing.news_id == rr).first()
        if id ==None:
            m1 = Dianjing(createtime=res[i]["createtime"],filename=res[i]["filename"],thumbnail= res[i]["thumbnail"],title=res[i]["title"],type=res[i]["type"],url=res[i]["url"],way=res[i]["way"],news_id=res[i]["id"])  # 再创建一个 Movie 记录
            db.session.add(m1)
            db.session.commit()

        else:
            print("news_id已存在") 
        time.sleep(0.5)
        # print(type(res[i]["filename"]))
        # print(db.session.query(Dianjing).filter_by(filename=res[i]["filename"]).first().filename)
        # print(type(db.session.query(Dianjing).filter_by(filename=res[i]["filename"]).first().filename))
        # if res[i]["filename"] == db.session.query(Dianjing).filter(Dianjing.filename==res[i]["filename"]).first().filename:
        #     print("filename已存在")
        # else:
        #     m1 = Dianjing(createtime=res[i]["createtime"],filename=res[i]["filename"],thumbnail= res[i]["thumbnail"],title=res[i]["title"],type=res[i]["type"],url=res[i]["url"],way=res[i]["way"])  # 再创建一个 Movie 记录
        #     db.session.add(m1)
        #     db.session.commit()
        time_now = time.strftime("%Y%m%d%H%M%S", time.localtime())

    # sum = len()
    lis_num=0
    for i in zhibo.dianjing_info():
        time.sleep(0.1)
        now=datetime.datetime.now()
        random_name=now.strftime("%Y%m%d%H%M%S")
        html_name = lis_way[::-1][lis_num]
        if not os.path.exists(f"{html_name}.htm"):
            with open(f'./static/game/{html_name}.htm','w',encoding="utf-8") as f:
                f.write(i)
        # oldname = f'./game/{html_name}.txt'
        # newname = f'./game/{html_name}.html'

        # os.rename(oldname, newname)
        time.sleep(0.1)
        # os.remove(newname)
        lis_num+=1

# @app.route('/htmlfile', methods=['GET'])
# def get_local_dianjing(start,end): 
    baseurl = "http://192.168.31.111:5000"


    data = get_file_List("./static/game/")[-50:]

    data_ctime = []
    num = len(data)
    for i in range(num):
        modelp = os.path.join("/static/game/", data[i])  # 拼接路径 
        data_ctime.append(modelp)
    # response = {
    #     "data":data_ctime,
    #     "code":200,
    #     "msg":"执行成功"        
    # }

    for i in data_ctime: 
        final_string_1 = i[-17:-4]
        final_string_2 = i[-46:-4]
        final_string_3 = i[-16:-4]

        print("final_string_1=",final_string_1)
        print("final_string_2=",final_string_2)

        print("final_string_3=",final_string_3)

        rule = or_(Dianjing.filename == final_string_1,Dianjing.way == final_string_2,Dianjing.filename == final_string_3)
        dianjing = db.session.query(Dianjing).filter(rule).first()
        if dianjing != None:
            dianjing.url = i
            db.session.commit()
    db.session.close()





@app.route('/dianjing', methods=['GET'])
@auto_rollback
def get_dianjing():
    db.session.remove()
    db.engine.dispose() 
    res =  db.session.query(Dianjing).all()[::-1]#倒序[::-1]
    
    total = db.session.query(Dianjing).count()
    currentPage = int(request.args.get("currentPage"))
    pageSize = int(request.args.get("pageSize"))
    start_data = (currentPage-1)*pageSize
    end_data = currentPage*pageSize
    temp=[]
    for x in res:
        temp.append(x.to_json())
    temp = temp[start_data:end_data]
    print(temp)
    response = {
        "code":200,
        "data":temp,
        "total":total,
        "totalPages":total % 10,
        "msg":"执行成功"
    }

    return jsonify(response)


# 定时任务
# 每隔2分钟执行
scheduler.add_job(func=check_insert_data, id='job1', trigger='interval', minutes=3)
 
# 11点-15点 每隔20分钟执行）
# scheduler.add_job(func=job_func, id='job2', trigger='cron',
#                   hour='11-15', minute='*/20')
 
# 每日13点30分执行
# scheduler.add_job(func=job_func, id='job3', trigger='cron', hour=13, minute=30, )
 
# scheduler.init_app(app)  # APScheduler 把任务列表放进flask
scheduler.start()  # 启动任务列表

if __name__ == '__main__':

    # db.drop_all() #删表
    # db.create_all() #新建表
    # data = movie_info(0,100)[0] #爬虫接口前100个数据
    # n = len(data)
    # oss = OssfileUrl()
    # pic_list = oss.get_oss_moviePicList(101) # 把oss文件按修改时间排序
    #插入数据库
    # for i in range(n):
    #     #这里strip将解析每一个字符，检查首尾是否存在，存在就去除返回
    #     m1 = Movie(cover_url=pic_list[i],title=data[i]["title"],release_date= data[i]["release_date"],score=data[i]["score"],actors=str(data[i]["actors"]).strip('[]'))  # 再创建一个 Movie 记录
    #     db.session.add(m1)
    # db.session.commit()
    # scheduler=APScheduler()
    # scheduler.init_app(app)
    # scheduler.start()
    app.run(debug=True,host='0.0.0.0')
    
