import sqlite3
import json
from flask import Flask, render_template, request, url_for, redirect, session
from flask_session import Session
import requests


def get_db_connection():  # izmeniti posle
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

app = Flask(__name__)
SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
Session(app)
app.config['SECRET_KEY'] = 'e57c08e5c755790bcaa474f8'

@app.route('/')
def index():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    users = [dict(row) for row in users]
    return json.dumps(users) 
    
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

@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST': #proveri je l mora
        body = request.data
        response = json.loads(body)
        username = response['username']
        password = response['password']
        conn = get_db_connection()
        attempted_user = conn.execute(
            "SELECT * FROM users WHERE username=? AND password_hash=?", [username, password]).fetchone()
        
        if attempted_user:
            authenticated_user = dict(attempted_user)
            current_user_id = authenticated_user['id']
            session['user_id'] = current_user_id

    return (session['user_id'])

@app.route('/newpost', methods=('GET', 'POST'))
def new_post():
    current_user_id = session['user_id']
    if request.method == 'POST':
        payload = {'title': 'bla',
                   'content': 'blablabla',
                   'user_id': current_user_id}
        r = requests.post('http://127.0.0.1:3000/create', json=payload)
        return (payload)
    

""" @app.route('/profile/<id>')
def user_profile():
    # GET all posts from a user with current id """

