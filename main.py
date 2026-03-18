import os, sqlite3, telebot, random, threading
from telebot import types
from flask import Flask, render_template_string

# --- ТАНЗИМОТИ ШЕФ ---
TOKEN = '8780142915:AAE7lMwsS4O1S5V2MhOmn2JQ3Nf_iZDifcQ'
ADMIN_ID = 6967256070 
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

# --- БАЗАИ МАЪЛУМОТ (31 ФУНКСИЯ) ---
def db_query(sql, params=()):
    with sqlite3.connect('shef_imperial.db', check_same_thread=False) as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        return cursor.fetchall()

db_query('''CREATE TABLE IF NOT EXISTS users 
           (id INTEGER PRIMARY KEY, name TEXT, balance REAL DEFAULT 0, 
            points REAL DEFAULT 0, vault REAL DEFAULT 0, 
            badge TEXT DEFAULT '', inventory TEXT DEFAULT '', 
            internal_number INTEGER, status TEXT DEFAULT 'active')''')

# --- HTML (WEB APP) ДАР ДОХИЛИ КОД (БАРОИ БЕХАТО КОР КАРДАН) ---
HTML_CODE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { background: #000; color: #f1c40f; font-family: sans-serif; text-align: center; margin: 0; overflow: hidden; }
        .header { padding: 20px; border-bottom: 2px solid #f1c40f; font-size: 1.2em; background: #111; }
        .score { font-size: 3em; margin: 40px 0; font-weight: bold; text-shadow: 0 0 15px gold; }
        .coin { width: 200px; cursor: pointer; transition: 0.1s; -webkit-tap-highlight-color: transparent; }
        .coin:active { transform: scale(0.95); }
        .stats { color: #00ffcc; font-size: 0.9em; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="header">💎 SHEFCOIN MINING</div>
    <div class="score" id="s">0.00</div>
    <div class="stats">⚡️ СУРЪАТ: +0.05 / ТАП</div>
    <img src="https://img.icons8.com/clouds/200/diamond.png" class="coin" onclick="m()">
    <script>
        let p = 0;
        function m() {
            p += 0.05;
            document.getElementById('s').innerText = p.toFixed(2);
            if(window.Telegram && window.Telegram.WebApp) window.Telegram.WebApp.HapticFeedback.impactOccurred('medium');
        }
    </script>
</body>
</html>
"""

@server.route('/')
def index():
    return render_template_string(HTML_CODE)

# --- ЛОГИКАИ БОТ ---
def main_menu(uid):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(types.KeyboardButton("🚀 КУШОДАНИ SHEF APP", web_app=types.WebAppInfo("https://" + os.environ.get('RENDER_EXTERNAL_HOSTNAME', 'localhost'))))
    markup.add('🏦 Сандуқи Махфӣ', '🎒 Инвентар')
    markup.add('🏆 Рейтинги Глобалӣ', '🔄 Табдилдиҳии Хол')
    markup.add('💬 Чат-Рулёт (NEW)', '⚙️ Танзимоти Система')
    if uid == ADMIN_ID: markup.add('🛡 ПАНЕЛИ АДМИН')
    return markup

@bot.message_handler(commands=['start'])
def start(m):
    uid = m.from_user.id
    user = db_query("SELECT internal_number FROM users WHERE id=?", (uid,))
    if not user:
        last = db_query("SELECT MAX(internal_number) FROM users")[0][0]
        new_n = 1 if last is None else last + 1
        if uid == ADMIN_ID: new_n = 1
        db_query("INSERT INTO users (id, name, internal_number, badge) VALUES (?, ?, ?, ?)", 
                 (uid, m.from_user.first_name, new_n, "👑 SHEF" if uid == ADMIN_ID else ""))
        num = new_n
    else: num = user[0][0]
    
    bot.send_message(m.chat.id, f"🛰 **SHEFCOIN v31.0**\n🆔 ID: `ID-{str(num).zfill(6)}`", 
                     reply_markup=main_menu(uid), parse_mode='Markdown')

# 🏦 САНДУҚ
@bot.message_handler(func=lambda m: m.text == '🏦 Сандуқи Махфӣ')
def vault(m):
    res = db_query("SELECT balance, vault FROM users WHERE id=?", (m.from_user.id,))
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📥 Мондан", callback_data="in"), types.InlineKeyboardButton("📤 Гирифтан", callback_data="out"))
    bot.send_message(m.chat.id, f"🏦 **Сейф:**\n💰 Баланс: {res[0][0]}\n🔒 Сандуқ: {res[0][1]}", reply_markup=markup)

# ⚙️ ТАНЗИМОТ (BURN)
@bot.message_handler(func=lambda m: m.text == '⚙️ Танзимоти Система')
def settings(m):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("❌ НЕСТ КАРДАНИ ПРОФИЛ", callback_data="burn"))
    bot.send_message(m.chat.id, "⚙️ Танзимоти махфият:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "burn")
def burn(call):
    db_query("DELETE FROM users WHERE id=?", (call.from_user.id,))
    bot.answer_callback_query(call.id, "Профил сӯхт!", show_alert=True)
    bot.send_message(call.message.chat.id, "Барои оғози нав: /start")

# 🏆 РЕЙТИНГ
@bot.message_handler(func=lambda m: m.text == '🏆 Рейтинги Глобалӣ')
def rank(m):
    users = db_query("SELECT name, points, badge FROM users ORDER BY points DESC LIMIT 10")
    txt = "🏆 **ТОП-10 МАЙНЕРОН:**\n\n"
    for i, u in enumerate(users, 1): txt += f"{i}. {u[2]} {u[0]} — {u[1]:.2f} pts\n"
    bot.send_message(m.chat.id, txt, parse_mode='Markdown')

# RUN SERVER & BOT
def run_flask():
    port = int(os.environ.get("PORT", 5000))
    server.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.infinity_polling()
