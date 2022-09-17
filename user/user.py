from lib2to3.pgen2 import token
import sqlite3
import json
from flask import Flask, request, jsonify, make_response
import jwt 
import datetime
import requests
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

def get_db_connection():  # izmeniti posle
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = 'e57c08e5c755790bcaa474f8'

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message': 'Token is missing'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")
            conn = get_db_connection()
            current_user = conn.execute(
            f"SELECT * FROM users WHERE id='{data['id']}'").fetchone()
            current_user = dict(current_user)
        except:
            return jsonify({'mesage': 'Token is invalid'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

@app.route('/')
def index():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    users = [dict(row) for row in users]
    return json.dumps(users)

@app.route('/unprotected')
def unprotected():
    return jsonify({'message': 'Anyone can view this'})

@app.route('/protected')
@token_required
def protected(current_user):
    return current_user

@app.route('/register', methods=['POST'])
def register_page():
    data = request.get_json()

    hashed_password = generate_password_hash(data['password'], method='sha256')

    username = data['username']
    email_address = data['email_address']
    password = hashed_password

    conn = get_db_connection()
    conn.execute("INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                     (username, email_address, password))
    conn.commit()
    conn.close()

    return jsonify({'message': 'New user created'})


@app.route('/login')
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify!', 401, {'WWW-Authenticate' : 'Basic realm="Login Required"'})

    conn = get_db_connection()

    user = conn.execute(
        f"SELECT * FROM users WHERE username='{auth.username}'").fetchone()
    if not user:
        return make_response('Could not verify!', 401, {'WWW-Authenticate' : 'Basic realm="Login Required"'})

    user = dict(user)
    password = user['password_hash']
    user_id = user['id']

    if check_password_hash(password, auth.password):
        token = jwt.encode({ 'id' : user_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
        
        return jsonify({'token' : token})
    
    return make_response('Could not verify!', 401, {'WWW-Authenticate' : 'Basic realm="Login Required"'})


@app.route('/newpost', methods=['POST'])
@token_required
def new_post(current_user):
        payload = {'title': 'JWT',
                   'content': 'JWT Auth Test 2',
                   'user_id': current_user['id']}
        r = requests.post('http://127.0.0.1:5000/create', json=payload)
        return (payload)
    

""" @app.route('/profile/<id>')
def user_profile():
    # GET all posts from a user with current id """
