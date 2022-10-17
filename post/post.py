from lib2to3.pgen2 import token
import sqlite3
from flask import Flask, request, jsonify
from functools import wraps
import jwt

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

app = Flask(__name__)
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
            f"SELECT * FROM posts WHERE user_id='{data['user_id']}'").fetchone()
            current_user = dict(current_user)
        except:
            return jsonify({'mesage': 'Token is invalid'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

@app.route('/')
def index():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    posts = [dict(row) for row in posts]

    return jsonify(posts)

@app.route('/create', methods=['POST'])
def create_post():
    data = request.get_json()
    title = data['title']
    content = data['content']
    user_id = data['user_id']

    conn = get_db_connection()
    conn.execute("INSERT INTO posts (title, content, user_id) VALUES (?, ?, ?)", (title, content, user_id))
    conn.commit()
    conn.close()

    return (data)

@app.route('/posts/<user_id>')
def get_posts(user_id):
    conn = get_db_connection()
    posts = conn.execute(f"SELECT * FROM posts where user_id='{user_id}'").fetchall()
    conn.close()
    posts = [dict(row) for row in posts]

    return jsonify(posts)



@app.route('/remove/<id>', methods=['DELETE'])
@token_required
def delete_post(current_user, id):
    conn = get_db_connection()
    conn.execute(f"DELETE FROM posts WHERE id ='{id}'")
    conn.commit()
    conn.close()

    return jsonify({"message" : "Post deleted sucessfully"})

@app.route('/update/<id>', methods=['PUT'])
@token_required
def update_post(current_user, id):
    data = request.get_json()
    conn = get_db_connection()
    post = conn.execute(
        f"SELECT * FROM posts WHERE id='{id}'").fetchone()
    post = dict(post)
    updated_title = data['title']
    updated_content = data['content']
    conn.execute(f"UPDATE posts SET title = '{updated_title}', content = '{updated_content}' WHERE id='{id}'")
    conn.commit()
    conn.close()

    return jsonify(post)

    

    
