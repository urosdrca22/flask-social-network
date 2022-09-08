import sqlite3
import json
from flask import Flask, request, render_template

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