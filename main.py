import os, sqlite3, telebot, random
from telebot import types

TOKEN = '8780142915:AAE7lMwsS4O1S5V2MhOmn2JQ3Nf_iZDifcQ'
ADMIN_ID = 6967256070 
WEB_URL = "https://shefcoin-app.onrender.com" 

bot = telebot.TeleBot(TOKEN)

# --- БАЗАИ МАЪЛУМОТ ---
def db_query(sql, params=()):
    with sqlite3.connect('shef_ghost_v30.db', check_same_thread=False) as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        return cursor.fetchall()

db_query('''CREATE TABLE IF NOT EXISTS users 
           (id INTEGER PRIMARY KEY, name TEXT, balance REAL DEFAULT 0, 
            points REAL DEFAULT 0, vault REAL DEFAULT 0, 
            badge TEXT DEFAULT '', inventory TEXT DEFAULT '', 
            internal_number INTEGER)''')

# --- МЕНЮҲО ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(types.KeyboardButton("🚀 КУШОДАНИ SHEF APP", web_app=types.WebAppInfo(WEB_URL)))
    markup.row('🏦 Сандуқ', '🎒 Инвентар', '🏆 Рейтинг')
    markup.row('💬 Чат-Рулёт', '⚙️ Танзимот')
    return markup

@bot.message_handler(commands=['start'])
def start(m):
    uid = m.from_user.id
    name = m.from_user.first_name
    
    user = db_query("SELECT internal_number FROM users WHERE id=?", (uid,))
    
    if not user:
        last_num = db_query("SELECT MAX(internal_number) FROM users")[0][0]
        new_num = 1 if last_num is None else last_num + 1
        if uid == ADMIN_ID: new_num = 1
        
        db_query("INSERT INTO users (id, name, internal_number, badge) VALUES (?, ?, ?, ?)", 
                 (uid, name, new_num, "👑 SHEF" if uid == ADMIN_ID else ""))
        current_num = new_num
    else:
        current_num = user[0][0]

    formatted_id = f"ID-{str(current_num).zfill(6)}"
    bot.send_message(m.chat.id, f"🛰 **SHEFCOIN v30.0**\n\n🆔 Рақами махфии шумо: `{formatted_id}`\n\nХуш омадед ба Империяи махфӣ!", reply_markup=main_menu(), parse_mode='Markdown')

# --- ⚙️ ТАНЗИМОТ ВА НЕСТ КАРДАН ---
@bot.message_handler(func=lambda m: m.text == '⚙️ Танзимот')
def settings(m):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("❌ Нест кардани Профил", callback_data="delete_profile"))
    bot.send_message(m.chat.id, "⚙️ **Танзимоти профил:**\n\nОгоҳӣ: Агар профилро нест кунед, ҳамаи холҳо ва ID-и шумо абадӣ тоза мешаванд.", reply_markup=markup, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data == "delete_profile")
def delete_confirm(call):
    uid = call.from_user.id
    db_query("DELETE FROM users WHERE id=?", (uid,))
    bot.answer_callback_query(call.id, "🗑 Профили шумо нест карда шуд!", show_alert=True)
    bot.send_message(call.message.chat.id, "🚪 Шумо Империяро тарк кард ва ҳама чиз сӯхт. Барои аз нав сар кардан /start-ро пахш кунед.")

# --- 🏆 РЕЙТИНГ (МАХФӢ) ---
@bot.message_handler(func=lambda m: m.text == '🏆 Рейтинг')
def leaderboard(m):
    # Дар ин ҷо internal_number-ро нишон намедиҳем, то махфӣ монад
    users = db_query("SELECT name, points, badge FROM users ORDER BY points DESC LIMIT 10")
    text = "🏆 **ТОП-10 МАЙНЕРОНИ МАХФӢ:**\n\n"
    for i, u in enumerate(users, 1):
        text += f"{i}. {u[2]} {u[0]} — `{u[1]:.2f} хол` \n"
    bot.send_message(m.chat.id, text, parse_mode='Markdown')

# --- 💬 ДИГАР ФУНКСИЯҲО ---
@bot.message_handler(func=lambda m: m.text in ['🏦 Сандуқ', '🎒 Инвентар', '💬 Чат-Рулёт'])
def handle_all(m):
    uid = m.from_user.id
    if m.text == '🏦 Сандуқ':
        res = db_query("SELECT balance, vault FROM users WHERE id=?", (uid,))
        bot.send_message(m.chat.id, f"🏦 Сандуқи шумо:\n💰 Баланс: {res[0][0]} TJS\n🔒 Маҳфуз: {res[0][1]} TJS")
    elif m.text == '🎒 Инвентар':
        res = db_query("SELECT inventory FROM users WHERE id=?", (uid,))
        bot.send_message(m.chat.id, f"🎒 Инвентар: {res[0][0] if res[0][0] else 'Холӣ'}")
    elif m.text == '💬 Чат-Рулёт':
        bot.send_message(m.chat.id, "🔍 Ҷустуҷӯи ҳамсӯҳбати махфӣ...")

bot.infinity_polling()
