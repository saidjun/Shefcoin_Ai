import os, threading, sqlite3, telebot, time, random
import google.generativeai as genai
from flask import Flask, render_template

# --- ТАНЗИМОТ ---
TOKEN = '8780142915:AAE7lMwsS4O1S5V2MhOmn2JQ3Nf_iZDifcQ'
API_KEY = 'AIzaSyAF (Калиди Gemini-и шумо)'
ADMIN_ID = 6967256070 

bot = telebot.TeleBot(TOKEN)
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')
app = Flask(__name__)

# --- БАЗАИ МАЪЛУМОТ (V14) ---
def db_query(sql, params=()):
    with sqlite3.connect('shefcoin_final_boss.db', check_same_thread=False) as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        return cursor.fetchall()

db_query('''CREATE TABLE IF NOT EXISTS users 
           (id INTEGER PRIMARY KEY, name TEXT, balance REAL, vip INTEGER, vpn_exp INTEGER, photo TEXT, bio TEXT)''')
db_query('''CREATE TABLE IF NOT EXISTS vouchers (code TEXT PRIMARY KEY, amount REAL)''')
db_query('''CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)''')

# --- WEB SERVER ---
@app.route('/')
def index(): return render_template('index.html')

# --- МЕНЮИ WHATSAPP STYLE ---
def main_markup(uid):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('👤 Профили Ман', '💬 Чатҳо', '🤖 AI Gemini')
    markup.row('👑 VIP Зинаҳо', '🛡 VPN Premium')
    markup.row('💳 Баланс / QR', '🎟 Ваучер', '🎧 Дастгирии Зинда 🛡')
    markup.row('📊 Асъор', '🛠 Конструктор', '⭐️ Отзывҳо')
    if uid == ADMIN_ID: markup.row('👑 Панели Админ', '➕ Сохтани Ваучер', '📸 Ивази QR')
    return markup

@bot.message_handler(commands=['start'])
def start(m):
    db_query("INSERT OR IGNORE INTO users VALUES (?, ?, 0, 0, 0, NULL, 'Дар Shefcoin Super-App')", 
             (m.from_user.id, m.from_user.first_name))
    
    welcome_text = (f"🚀 **Shefcoin OS v14.0**\n\n"
                    f"🔥 Онлайн: {random.randint(50, 150)} нафар\n"
                    f"✅ Системаи верификатсияшуда фаъол аст.\n\n"
                    f"Хуш омадед, {m.from_user.first_name}!")
    bot.send_message(m.chat.id, welcome_text, reply_markup=main_markup(m.from_user.id), parse_mode='Markdown')

# --- 🎧 ДАСТГИРИИ ЗИНА (GHOST MODERATOR) ---
@bot.message_handler(func=lambda m: m.text == '🎧 Дастгирии Зинда 🛡')
def support_gate(m):
    text = ("🛡 **Маркази дастгирии Shefcoin**\n\n"
            "👤 Модератор: *Онлайн* ✅\n"
            "⏱ Вақти ҷавоб: ~2 дақиқа\n\n"
            "Лутфан мушкилӣ ё саволи худро нависед:")
    msg = bot.reply_to(m, text, parse_mode='Markdown')
    bot.register_next_step_handler(msg, send_to_mod)

def send_to_mod(m):
    # Фиристодан ба ту (Админ)
    bot.send_message(ADMIN_ID, f"📩 **ПАЁМИ НАВ БА МОДЕРАТОР:**\nID: `{m.from_user.id}`\nНом: {m.from_user.first_name}\n\nМатн: {m.text}\n\n*(Reply кунед барои ҷавоб)*", parse_mode='Markdown')
    bot.reply_to(m, "✅ **Фиристода шуд!** Модератор ҳозир паёми шуморо мехонад...")

# --- ⚡️ ҶАВОБИ МОДЕРАТОР (REPLY SYSTEM) ---
@bot.message_handler(func=lambda m: m.reply_to_message is not None and m.from_user.id == ADMIN_ID)
def mod_reply(m):
    try:
        # Ёфтани ID-и корбар аз матни паёми қаблӣ
        u_id = int(m.reply_to_message.text.split('ID: ')[1].split('\n')[0].replace('`', ''))
        
        # Эффекти "Typing" дар чати корбар
        bot.send_chat_action(u_id, 'typing')
        time.sleep(2) # Каме таваққуф барои боварӣ
        
        reply_text = f"🛡 **Official Support Team** ✅\n\n{m.text}"
        bot.send_message(u_id, reply_text)
        bot.reply_to(m, "✅ Ҷавоби модератор расонида шуд!")
    except:
        bot.reply_to(m, "❌ Хато! Танҳо ба паёмҳои Дастгирӣ 'Reply' кунед.")

# --- 👑 VIP ЗИНАҲО БО АСЪОР ---
@bot.message_handler(func=lambda m: m.text == '👑 VIP Зинаҳо')
def vip_details(m):
    text = ("🏆 **Нақшаҳои Премиум:**\n\n"
            "🥉 Silver: 30 TJS / 250 RUB / 3 USD\n"
            "🥈 Gold: 60 TJS / 500 RUB / 6 USD\n"
            "🥇 Platinum: 120 TJS / 1000 RUB / 12 USD\n\n"
            "💎 Хариди VIP = VPN-и доимӣ + AI-и пурқувват.")
    bot.reply_to(m, text)

# --- AI GEMINI (GHOST MODE) ---
@bot.message_handler(func=lambda m: True)
def ai_brain(m):
    if m.text in ['👤 Профили Ман', '💬 Чатҳо', '🎧 Дастгирии Зинда 🛡']: return
    think = bot.reply_to(m, "🧠 *Фикр...*")
    try:
        res = model.generate_content(m.text)
        bot.edit_message_text(res.text, m.chat.id, think.message_id)
    except:
        bot.edit_message_text("❌ Хато", m.chat.id, think.message_id)

if __name__ == '__main__':
    threading.Thread(target=lambda: bot.infinity_polling()).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
