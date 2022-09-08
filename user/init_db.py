import sqlite3

connection = sqlite3.connect('database.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            ('Uros', 'Uros@uros.com', 'uros123')
            )

cur.execute("INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            ('Jovana', 'Jovana@jovana.com', 'uros123')
            )

connection.commit()
connection.close()