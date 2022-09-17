from lib2to3.pgen2 import token
import sqlite3
import json
from flask import Flask, render_template, request, jsonify, make_response
import jwt 
import datetime
import requests
from functools import wraps


def get_db_connection():  # izmeniti posle
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

app = Flask(__name__)
SESSION_TYPE = 'filesystem'
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

@app.route('/register', methods=('GET', 'POST'))
def register_page():
    if request.method == 'POST':
        body = request.data
        response = json.loads(body)
        print(response)

        username = response['username']
        email_address = response['email_address']
        password1 = response['password1']
        password2 = response['password2']

        conn = get_db_connection()
        conn.execute("INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                     (username, email_address, password1))
        conn.commit()
        conn.close()

    return render_template('register.html')


@app.route('/login')
def login():
    auth = request.authorization
    if auth:
        conn = get_db_connection()
        user = conn.execute(
            f"SELECT * FROM users WHERE username='{auth.username}'").fetchone()
        user = dict(user)
        user_id = user['id']
        token = jwt.encode({ 'id' : user_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
        return jsonify({'token' : token})

    return make_response('Could not verify!', 401, {'WWW-Authenticate' : 'Basic realm="Login Required"'})

    

@app.route('/newpost', methods=['POST'])
@token_required
def new_post(current_user):
        payload = {'title': 'JWT',
                   'content': 'JWT Auth Test ',
                   'user_id': current_user['id']}
        r = requests.post('http://127.0.0.1:5000/create', json=payload)
        return (payload)
    

""" @app.route('/profile/<id>')
def user_profile():
    # GET all posts from a user with current id """
