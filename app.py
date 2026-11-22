import os
import sqlite3
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY, 
        fullname TEXT, 
        phone TEXT, 
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    try:
        c.execute("INSERT OR REPLACE INTO users (user_id, fullname, phone) VALUES (?, ?, ?)", 
                  (data['user_id'], data['fullname'], data['phone']))
        conn.commit()
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
