import sqlite3
import json
from flask import Flask, request, jsonify

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

app = Flask(__name__)

@app.route('/')
def index():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    posts = [dict(row) for row in posts]
    return json.dumps(posts)

@app.route('/create', methods=('GET', 'POST'))
def create_post():
    if request.method == 'POST':
        body = request.data
        response = json.loads(body)
        print (response)

        title = response['title']
        content = response['content']
        user_id = response['user_id']

        conn = get_db_connection()
        conn.execute("INSERT INTO posts (title, content, user_id) VALUES (?, ?, ?)", (title, content, user_id))
        conn.commit()
        conn.close()

    return (response)

@app.route('/posts/<user_id>')
def get_posts(user_id):
    conn = get_db_connection()
    posts = conn.execute(f"SELECT * FROM posts where user_id='{user_id}'").fetchall()
    posts = [dict(row) for row in posts]
    return jsonify(posts)

@app.route('/remove/<id>', methods=['DELETE'])
def delete_post(id):
    conn = get_db_connection()
    conn.execute(f"DELETE FROM posts WHERE id ='{id}'")
    conn.commit()
    conn.close()
    return jsonify({"message" : "Post deleted sucessfully"})