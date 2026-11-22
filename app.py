import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes
import asyncio

app = Flask(__name__)

# ⚠️ توکن خود را اینجا بگذارید
TOKEN = "توکن_ربات_خود_را_اینجا_بگذارید" 
# ⚠️ لینک Render خود را اینجا بگذارید
WEB_APP_URL = "https://asadi-miniapp.onrender.com" 

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

# این تابع وب‌هوک را تنظیم می‌کند تا ربات و سایت همزمان بدون مشکل کار کنند
@app.route(f"/{TOKEN}", methods=['POST'])
async def telegram_webhook():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    
    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.initialize()
    await application.process_update(update)
    return "ok"

@app.route('/set_webhook')
def set_webhook():
    # این آدرس را یک بار در مرورگر باز کنید تا ربات به سرور متصل شود
    import requests
    webhook_url = f"https://asadi-miniapp.onrender.com/{TOKEN}"
    response = requests.get(f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={webhook_url}")
    return response.json()

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
