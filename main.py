import os, sqlite3, telebot, random, time
from telebot import types

# МАЪЛУМОТИ ТУ
TOKEN = '8780142915:AAE7lMwsS4O1S5V2MhOmn2JQ3Nf_iZDifcQ'
ADMIN_ID = 6967256070 
WEB_URL = "https://shefcoin-app.onrender.com" 

bot = telebot.TeleBot(TOKEN)

# --- 1. БАЗАИ МАЪЛУМОТ (Ҳамаи сутунҳо) ---
def db_query(sql, params=()):
    with sqlite3.connect('shef_final_v31.db', check_same_thread=False) as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        return cursor.fetchall()

db_query('''CREATE TABLE IF NOT EXISTS users 
           (id INTEGER PRIMARY KEY, 
            name TEXT, 
            balance REAL DEFAULT 0, 
            points REAL DEFAULT 0, 
            vault REAL DEFAULT 0, 
            badge TEXT DEFAULT '', 
            inventory TEXT DEFAULT '', 
            internal_number INTEGER)''')

# --- 2. МЕНЮИ АСОСӢ (Reply Markup) ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(types.KeyboardButton("🚀 КУШОДАНИ SHEF APP", web_app=types.WebAppInfo(WEB_URL)))
    markup.row('🏦 Сандуқи Махфӣ', '🎒 Инвентар')
    markup.row('🏆 Рейтинг', '🔄 Табдилдиҳӣ')
    markup.row('💬 Чат-Рулёт (NEW)', '⚙️ Танзимот')
    return markup

# --- 3. САРШАВӢ ВА ID-И МАХФӢ ---
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
    bot.send_message(m.chat.id, f"🛰 **SHEFCOIN v31.0**\n\n🆔 Рақами махфии шумо: `{formatted_id}`", 
                     reply_markup=main_menu(), parse_mode='Markdown')

# --- 4. САНДУҚИ МАХФӢ (Vault Logic) ---
@bot.message_handler(func=lambda m: m.text == '🏦 Сандуқи Махфӣ')
def vault_manager(m):
    res = db_query("SELECT balance, vault FROM users WHERE id=?", (m.from_user.id,))
    bal, vlt = res[0]
    text = f"🏦 **Сандуқи шумо:**\n💰 Баланси асосӣ: `{bal}` TJS\n🔒 Дар сандуқ: `{vlt}` TJS"
    
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("📥 Ба сандуқ", callback_data="v_in"),
               types.InlineKeyboardButton("📤 Аз сандуқ", callback_data="v_out"))
    bot.send_message(m.chat.id, text, reply_markup=markup, parse_mode='Markdown')

# --- 5. ТАНЗИМОТ ВА НЕСТ КАРДАН (Privacy) ---
@bot.message_handler(func=lambda m: m.text == '⚙️ Танзимот')
def settings_page(m):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("❌ Нест кардани Профил", callback_data="delete_me"))
    bot.send_message(m.chat.id, "⚙️ **Танзимот:**\n\nАгар профилро нест кунед, рақами ID ва холҳоятон месузанд.", 
                     reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "delete_me")
def delete_process(call):
    db_query("DELETE FROM users WHERE id=?", (call.from_user.id,))
    bot.answer_callback_query(call.id, "🔥 Профил сӯхт!", show_alert=True)
    bot.send_message(call.message.chat.id, "🚪 Шумо Империяро тарк кардед. Барои оғози нав: /start")

# --- 6. РЕЙТИНГИ МАХФӢ (Бе нишон додани ID) ---
@bot.message_handler(func=lambda m: m.text == '🏆 Рейтинг')
def leaderboard(m):
    users = db_query("SELECT name, points, badge FROM users ORDER BY points DESC LIMIT 10")
    text = "🏆 **ТОП-10 МАЙНЕРОН:**\n\n"
    for i, u in enumerate(users, 1):
        text += f"{i}. {u[2]} {u[0]} — `{u[1]:.2f} хол` \n"
    bot.send_message(m.chat.id, text, parse_mode='Markdown')

# --- 7. ИНВЕНТАР ВА ПЕРЕВОД ---
@bot.message_handler(func=lambda m: m.text == '🎒 Инвентар')
def inventory_check(m):
    res = db_query("SELECT inventory FROM users WHERE id=?", (m.from_user.id,))
    bot.send_message(m.chat.id, f"🎒 **Борхалта:**\n{res[0][0] if res[0][0] else 'Холӣ'}")

@bot.message_handler(commands=['send'])
def transfer(m):
    try:
        _, to_id, amt, t_type = m.text.split()
        col = "balance" if t_type == "money" else "points"
        db_query(f"UPDATE users SET {col} = {col} - ? WHERE id = ?", (float(amt), m.from_user.id))
        db_query(f"UPDATE users SET {col} = {col} + ? WHERE id = ?", (float(amt), int(to_id)))
        bot.reply_to(m, "✅ Иҷро шуд!")
    except: bot.reply_to(m, "📝 Мисол: `/send ID 100 points`")

bot.infinity_polling()
