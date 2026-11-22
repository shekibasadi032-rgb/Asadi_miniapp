import os
import sqlite3
import urllib.request
from flask import Flask, render_template, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes
import asyncio

app = Flask(__name__)

# ⚠️ توکن ربات خود را اینجا بگذارید
TOKEN = "9076981892:AAGdpFZbM-TEitkRX9Sh1vUWSbLnCMdH-Z0"
WEB_APP_URL = "https://asadi-miniapp-1.onrender.com" 
ADMIN_ID = 8992677752

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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🚀 ورود به فرم ثبت‌نام", web_app=WebAppInfo(url=WEB_APP_URL))]]
    await update.message.reply_text("سلام! برای ساخت حساب کاربری روی دکمه زیر بزنید:", reply_markup=InlineKeyboardMarkup(keyboard))

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("⛔ شما دسترسی ندارید.")
        return
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT fullname, phone, user_id FROM users ORDER BY created_at DESC")
    users = c.fetchall()
    conn.close()

    if not users:
        await update.message.reply_text("📭 هنوز کاربری ثبت‌نام نکرده است.")
        return

    text = "📊 **لیست کاربران:**\n\n"
    for i, u in enumerate(users, 1):
        text += f"{i}. 👤 {u[0]}\n📞 {u[1]}\n🆔 {u[2]}\n➖➖➖➖➖➖\n"
    
    await update.message.reply_text(text, parse_mode="Markdown")

@app.route(f'/webhook/{TOKEN}', methods=['POST'])
def webhook():
    try:
        application = Application.builder().token(TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("admin", admin_panel))
        
        update = Update.de_json(request.get_json(force=True), application.bot)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(application.initialize())
        loop.run_until_complete(application.process_update(update))
        loop.run_until_complete(application.shutdown())
        
        return "ok", 200
    except Exception as e:
        print(f"Webhook Error: {e}")
        return "error", 500

@app.route('/set_webhook')
def set_webhook():
    # بدون نیاز به کتابخانه requests، با ابزار داخلی پایتون
    webhook_url = f"https://asadi-miniapp-1.onrender.com/webhook/{TOKEN}"
    url = f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={webhook_url}"
    try:
        response = urllib.request.urlopen(url)
        return response.read().decode()
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
