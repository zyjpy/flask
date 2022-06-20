import os
from flask import Flask, jsonify, render_template, request, url_for, redirect, flash,abort, g
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from passlib.apps import custom_app_context
from itsdangerous import TimedSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired
from flask_httpauth import HTTPBasicAuth
from app import *
from zhiboba import Zhiboba
HOST = '47.92.93.77'
PORT = '3306'
DATABASE = 'test'
USERNAME = 'root'
PASSWORD = 'aA171207'
app = Flask(__name__)
# app.config['UPLOAD_FOLDER'] = r"E:/FLASK/static"
CORS(app)
DB_URI = "mysql+pymysql://{username}:{password}@{host}:{port}/{db}?charset=utf8".format(username=USERNAME,password=PASSWORD, host=HOST,port=PORT, db=DATABASE)
db = SQLAlchemy(app)

basedir = os.path.abspath(os.path.dirname(__file__))
auth = HTTPBasicAuth()

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_ECHO'] = True

BASEDIR = basedir
CSRF_ENABLED = True
SECRET_KEY = 'jklklsadhfjkhwbii9/sdf\sdf' 
class User(db.Model):
    __tablename__ =  'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password = db.Column(db.String(128))
 
    # 密码加密
    def hash_password(self, password):
        self.password = custom_app_context.encrypt(password)
    
    # 密码解析
    def verify_password(self, password):
        return custom_app_context.verify(password, self.password)
 
    # 获取token，有效时间10min
    def generate_auth_token(self, expiration = 600):
        s = Serializer(app.config['SECRET_KEY'], expires_in = expiration)
        return s.dumps({ 'id': self.id })
 
    # 解析token，确认登录的用户身份
    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token
        user = User.query.get(data['id'])
        return user
@app.route("/")
@auth.login_required
def index():    
    return jsonify('Hello, %s' % g.user.username)
 
 
@app.route('/api/users', methods = ['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400) # missing arguments
    if db.session.query(User).filter_by(username = username).first() is not None:
        abort(400) # existing user

    user = User(username = username)
    
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({ 'username': user.username })
 
@auth.verify_password
def verify_password(username_or_token, password):
    if request.path == "/api/login":
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    else:
        user = User.verify_auth_token(username_or_token)
        if not user:
            return False    
    g.user = user   
    return True
 
 
@app.route('/api/login')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify(token)

class Dianjing(db.Model):
    __tablename__ =  'dianjing'
    id = db.Column(db.Integer, primary_key=True)
    createtime = db.Column(db.String(128))
    filename = db.Column(db.String(128))
    thumbnail = db.Column(db.String(128))
    title = db.Column(db.String(128))
    type = db.Column(db.String(128))
    url = db.Column(db.String(128))
    way = db.Column(db.String(128))
    news_id = db.Column(db.String(128))
    def to_json(self):
        return {
                'id': self.id,
                'createtime': self.createtime,
                'filename': self.filename,
                'thumbnail': self.thumbnail,
                'title': self.title,
                'type' : self.type,
                'url' : self.url,
                'way' : self.way,
                }
if __name__ == '__main__':

    db.drop_all()
    db.create_all() #新建表
    db.session.commit()
    app.run(debug=True,host='0.0.0.0')