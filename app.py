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

# وب‌سرور برای نمایش فرم
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

# تنظیمات ربات تلگرام
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🚀 ورود به فرم", web_app=WebAppInfo(url=WEB_APP_URL))]]
    await update.message.reply_text("برای ثبت‌نام روی دکمه زیر بزنید:", reply_markup=InlineKeyboardMarkup(keyboard))

def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(coro)

@app.route(f"/webhook/{TOKEN}", methods=['POST'])
def telegram_webhook():
    try:
        application = Application.builder().token(TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        
        update = Update.de_json(request.get_json(force=True), application.bot)
        
        async def process():
            await application.initialize()
            await application.process_update(update)
            await application.shutdown()
            
        run_async(process())
        return "ok", 200
    except Exception as e:
        print(f"Error: {e}")
        return "error", 500

@app.route('/set_webhook')
def set_webhook():
    import urllib.request
    webhook_url = f"https://asadi-miniapp.onrender.com/webhook/{TOKEN}"
    url = f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={webhook_url}"
    try:
        with urllib.request.urlopen(url) as response:
            return response.read().decode()
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
