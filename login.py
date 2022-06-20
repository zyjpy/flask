
from app import app, db, auth
from flask import render_template, json, jsonify, request, abort, g
from models import *
 
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
    if User.query.filter_by(username = username).first() is not None:
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
if __name__ == '__main__':
    from login import User
    # db.drop_all()
    # db.create_all() #新建表
    # db.session.commit()
    app.run(debug=True,host='0.0.0.0')