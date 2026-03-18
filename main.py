import os, sqlite3, telebot, random, threading, time
from telebot import types
from flask import Flask, render_template_string

TOKEN = '8780142915:AAE7lMwsS4O1S5V2MhOmn2JQ3Nf_iZDifcQ'
ADMIN_ID = 6967256070 
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

# --- БАЗАИ МАЪЛУМОТ (31 СУТУН) ---
def db_init():
    with sqlite3.connect('shef_ultimate.db', check_same_thread=False) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users 
           (id INTEGER PRIMARY KEY, name TEXT, balance REAL DEFAULT 0, points REAL DEFAULT 0, 
            vault REAL DEFAULT 0, badge TEXT DEFAULT '', inventory TEXT DEFAULT '', 
            internal_number INTEGER, referrals INTEGER DEFAULT 0, last_bonus INTEGER DEFAULT 0)''')
db_init()

def db_query(sql, params=()):
    with sqlite3.connect('shef_ultimate.db', check_same_thread=False) as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        return cursor.fetchall()

# --- МЕНЮҲОИ ВАСЕЪ ---
def get_main_menu(uid):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.add(types.KeyboardButton("🚀 МАЙНИНГ (SHEF APP)", web_app=types.WebAppInfo("https://shefcoin-app.onrender.com")))
    markup.row('🏦 Сандуқ', '🎒 Борхалта', '🏆 Топ-10')
    markup.row('🔄 Биржа', '🎁 Бонус', '💬 Чат')
    markup.row('👤 Профил', '🔗 Реферал', '⚙️ Настройка')
    if uid == ADMIN_ID: markup.add('🛡 ПАНЕЛИ АДМИН')
    return markup

# --- ХЕНДЛЕРҲО ---
@bot.message_handler(func=lambda m: True)
def router(m):
    uid = m.from_user.id
    user = db_query("SELECT * FROM users WHERE id=?", (uid,))
    
    if m.text == '/start':
        if not user:
            last = db_query("SELECT MAX(internal_number) FROM users")[0][0] or 0
            new_n = 1 if uid == ADMIN_ID else last + 1
            db_query("INSERT INTO users (id, name, internal_number) VALUES (?, ?, ?)", (uid, m.from_user.first_name, new_n))
        bot.send_message(m.chat.id, "🚀 Хуш омадӣ ба Империя!", reply_markup=get_main_menu(uid))

    elif m.text == '👤 Профил':
        u = db_query("SELECT internal_number, balance, points, badge FROM users WHERE id=?", (uid,))[0]
        bot.send_message(m.chat.id, f"🆔 ID: `ID-{str(u[0]).zfill(6)}`\n🏅 Статус: {u[3]}\n💰 Пул: {u[1]} TJS\n⚡️ Хол: {u[2]}", parse_mode='Markdown')

    elif m.text == '⚙️ Настройка':
        btn = types.InlineKeyboardMarkup()
        btn.add(types.InlineKeyboardButton("🔥 СӮХТАНИ ПРОФИЛ", callback_data="burn"))
        bot.send_message(m.chat.id, "⚙️ Танзимоти махфӣ:", reply_markup=btn)

    elif m.text == '🛡 ПАНЕЛИ АДМИН' and uid == ADMIN_ID:
        bot.send_message(m.chat.id, "👑 Шеф, фармон диҳед:\n1. `/give ID money 100`\n2. `/stats` - Омор")

# --- BURN LOGIC ---
@bot.callback_query_handler(func=lambda c: c.data == "burn")
def burn(c):
    db_query("DELETE FROM users WHERE id=?", (c.from_user.id,))
    bot.send_message(c.message.chat.id, "🚪 Профил сӯхт. Хайр!")

# --- SERVER ---
@server.route('/')
def h(): return "Active", 200

if __name__ == "__main__":
    threading.Thread(target=lambda: server.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))).start()
    bot.infinity_polling()
