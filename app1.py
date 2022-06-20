# -*- coding: utf-8 -*-
from calendar import c
from dataclasses import dataclass
from re import A
from traceback import print_tb
from webbrowser import get
from flask import Flask, jsonify, render_template, request, url_for, redirect, flash
from flask_cors import CORS
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy import JSON, TEXT, Text
app = Flask(__name__)
# cors = CORS(app, resources={"/getMsg": {"origins": "*"}})
cors = CORS(app)
import requests
import json # 用于处理json格式数据的模块
from flask_sqlalchemy import SQLAlchemy
from flask_paginate import Pagination, get_page_parameter

HOST = '47.92.93.77'
PORT = '3306'
DATABASE = 'test'
USERNAME = 'root'
PASSWORD = 'aA171207'

DB_URI = "mysql+pymysql://{username}:{password}@{host}:{port}/{db}?charset=utf8".format(username=USERNAME,password=PASSWORD, host=HOST,port=PORT, db=DATABASE)
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


class User(db.Model):  # 表名将会是 user（自动生成，小写处理）
    id = db.Column(db.Integer, primary_key=True)  # 主键
    name = db.Column(db.String(20))  # 名字

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

def movie_info(start=0,limit=30):
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
    return data


@app.route('/chart', methods=['GET', 'POST'])
def movie_list():
    from app import User, Movie
    res =  db.session.query(Movie).all()
    total = db.session.query(Movie).count()
    currentPage = int(request.args.get("currentPage"))
    pageSize = int(request.args.get("pageSize"))
    start_data = (currentPage-1)*pageSize
    end_data = currentPage*pageSize
    temp=[]
    for x in res:
        temp.append(x.to_json())
    temp = temp[start_data:end_data]
    return jsonify(temp,total)

@app.route('/searchMovie', methods=['GET', 'POST'])
def home():
    response = {
        'msg': 'Hello, Python !',
        "code":200,
        "data":{"a":1,"b":2}
    }
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
# movie_info()


@app.route('/movie', methods=['GET', 'POST'])
def get_movieinfo():
    response = {
        'msg': '末代皇帝',
        "code":200,
        "data":{"a":1,"b":2}
    }
    return jsonify(response)
if __name__ == '__main__':

    # db.drop_all()
    # db.create_all()
    # data = movie_info()
    # n = len(data)
    # for i in range(n):
    #     #这里strip将解析每一个字符，检查首尾是否存在，存在就去除返回
    #     m1 = Movie(cover_url=data[i]["cover_url"],title=data[i]["title"],release_date= data[i]["release_date"],score=data[i]["score"],actors=str(data[i]["actors"]).strip('[]'))  # 再创建一个 Movie 记录
    #     db.session.add(m1)
    # db.session.commit()
    app.run(debug=True,host='0.0.0.0')