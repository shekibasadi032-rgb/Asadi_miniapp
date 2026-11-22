
import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes
import threading

app = Flask(__name__)

# ⚠️ توکن خود را اینجا بگذارید
TOKEN = "9076981892:AAGdpFZbM-TEitkRX9Sh1vUWSbLnCMdH-Z0" 
# ⚠️ بعد از ساخت در Render، لینک را اینجا بگذارید
WEB_APP_URL = "https://asadi-miniapp.onrender.com/"
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, phone TEXT)""")
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
    c.execute("INSERT INTO users (name, phone) VALUES (?, ?)", (data['name'], data['phone']))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🚀 ورود به فرم", web_app=WebAppInfo(url=WEB_APP_URL))]]
    await update.message.reply_text("برای ثبت‌نام روی دکمه زیر بزنید:", reply_markup=InlineKeyboardMarkup(keyboard))

def run_bot():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.run_polling()

if __name__ == '__main__':
    init_db()
    threading.Thread(target=run_bot).start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
