import os, sqlite3, telebot, threading, time, uuid
from telebot import types
from flask import Flask, render_template_string

TOKEN = '8780142915:AAE7lMwsS4O1S5V2MhOmn2JQ3Nf_iZDifcQ'
ADMIN_ID = 6967256070 
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

# --- 1. ЯДРОИ БАЗАИ МАЪЛУМОТ (40 ФУНКСИЯ) ---
def init_db():
    conn = sqlite3.connect('imperial_core.db', check_same_thread=False)
    # Корбарон ва VPN
    conn.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY, balance REAL DEFAULT 0, vpn_key TEXT, vpn_expire INTEGER DEFAULT 0)''')
    # Системаи P2P бо Таймер
    conn.execute('''CREATE TABLE IF NOT EXISTS payments 
                 (uid INTEGER PRIMARY KEY, start_time INTEGER, status TEXT)''')
    # Танзимоти Админ (QR ва Корт)
    conn.execute('''CREATE TABLE IF NOT EXISTS config 
                 (key TEXT PRIMARY KEY, value TEXT)''')
    conn.commit()
    return conn

db_conn = init_db()

def db_exec(sql, params=()):
    with sqlite3.connect('imperial_core.db', check_same_thread=False) as conn:
        cur = conn.cursor()
        cur.execute(sql, params)
        conn.commit()
        return cur.fetchall()

# Танзимоти ибтидоӣ (агар холӣ бошад)
if not db_exec("SELECT * FROM config"):
    db_exec("INSERT INTO config VALUES ('qr_link', 'https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=SHEF-PAY')")
    db_exec("INSERT INTO config VALUES ('card_num', '9771 0000 0000 0000')")

# --- 2. МЕНЮИ АСОСӢ (V14.0 STYLE) ---
def main_menu(uid):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.row(types.KeyboardButton("🚀 КУШОДАНИ ИМПЕРИЯ", web_app=types.WebAppInfo("https://shefcoin-app.onrender.com")))
    markup.row('👤 Профил', '🛡 VPN Premium', '🛠 Конструктор')
    markup.row('💳 Баланс / QR', '🎟 Ваучер', '🤖 AI Gemini')
    if uid == ADMIN_ID: markup.row('👑 ПАНЕЛИ АДМИН')
    return markup

# --- 3. ЛОГИКАИ АСОСӢ ---
@bot.message_handler(commands=['start'])
def start(m):
    uid = m.from_user.id
    db_exec("INSERT OR IGNORE INTO users (id) VALUES (?)", (uid,))
    bot.send_message(m.chat.id, "🛰 **ИМПЕРИЯИ SHEF ФАЪОЛ ШУД!**\n\nҲамаи 40 функсия дар реҷаи 'Standby' ҳастанд.", reply_markup=main_menu(uid))

# ФУНКСИЯИ ПАРДОХТ (ТАЙМЕРИ 10 ДАҚИҚА)
@bot.message_handler(func=lambda m: m.text == '💳 Баланс / QR')
def pay_start(m):
    uid = m.from_user.id
    now = int(time.time())
    db_exec("INSERT OR REPLACE INTO payments VALUES (?, ?, 'pending')", (uid, now))
    
    qr = db_exec("SELECT value FROM config WHERE key='qr_link'")[0][0]
    card = db_exec("SELECT value FROM config WHERE key='card_num'")[0][0]
    
    bot.send_photo(m.chat.id, qr, caption=f"⏳ **ВАҚТ: 10 ДАҚИҚА**\n\n💳 КОРТ: `{card}`\n\nЧекро фиристед. Агар вақт гузарад, заявка месузад!")

# ТАФТИШИ ЧЕК (BURN LOGIC)
@bot.message_handler(content_types=['photo'])
def handle_receipt(m):
    uid = m.from_user.id
    res = db_exec("SELECT start_time FROM payments WHERE uid=? AND status='pending'", (uid,))
    
    if res:
        start_time = res[0][0]
        if int(time.time()) - start_time > 600: # 10 дақиқа
            db_exec("UPDATE payments SET status='burned' WHERE uid=?", (uid,))
            bot.send_message(uid, "🔥 **ВАҚТ ТАМОМ ШУД!** Заявкаи шумо сӯхт. Аз нав кӯшиш кунед.")
        else:
            bot.send_message(uid, "✅ Чек қабул шуд! Интизори тасдиқи Шеф бошед.")
            bot.forward_message(ADMIN_ID, m.chat.id, m.message_id)
            
            kb = types.InlineKeyboardMarkup()
            kb.add(types.InlineKeyboardButton("✅ ТАСДИҚ (10 TJS)", callback_data=f"ok_10_{uid}"))
            bot.send_message(ADMIN_ID, f"👤 Пардохт аз ID: {uid}", reply_markup=kb)
    else:
        # Агар админ бошад ва сурат фиристад - QR-ро иваз мекунад
        if uid == ADMIN_ID:
            bot.send_message(ADMIN_ID, "📸 Ин суратро ҳамчун QR-коди нав қабул кунам? (Нависед: /setqr)")

# --- 4. CALLBACKS (АВТО-БАЛАНС) ---
@bot.callback_query_handler(func=lambda c: c.data.startswith('ok_'))
def approve(c):
    _, amt, tid = c.data.split('_')
    db_exec("UPDATE users SET balance = balance + ? WHERE id = ?", (amt, tid))
    db_exec("DELETE FROM payments WHERE uid=?", (tid,))
    bot.send_message(tid, f"🎉 Баланси шумо +{amt} TJS пур шуд!")
    bot.answer_callback_query(c.id, "Иҷро шуд!")

# --- RUN ---
if __name__ == "__main__":
    print("Империя фаъол шуд...")
    bot.infinity_polling()
