import os
import threading
import telebot
import google.generativeai as genai
from flask import Flask, render_template

# 1. Танзимоти калидҳо (Мустақим)
TOKEN = '8780142915:AAE7lMwss401S5V2MhOmn2JQ3Nf_iZDifcQ'
API_KEY = 'AIzaSyDMA9WC1p8CwG3ABNcfPHLSpM_5AtAAFjk'

bot = telebot.TeleBot(TOKEN)
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro')

app = Flask(__name__)

# --- ҚИСМИ САЙТ (WEB) ---
@app.route('/')
def index():
    return render_template('index.html')

# --- ҲЕНДЛЕРҲОИ МЕНЮИ ТЕЛЕГРАМ ---

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "📱 Хуш омадед ба Super-App!\nҲамаи тугмаҳои меню фаъол шуданд. Чӣ хел кӯмак кунам?")

@bot.message_handler(commands=['profile'])
def profile(message):
    text = (f"👤 **Кабинети шахсӣ**\n\n"
            f"🆔 ID: `{message.from_user.id}`\n"
            f"👤 Ном: {message.from_user.first_name}\n"
            f"💰 Баланс: 0.00 TJS\n"
            f"🌟 Статус: Корбар")
    bot.reply_to(message, text, parse_mode='Markdown')

@bot.message_handler(commands=['edit_profile'])
def edit_profile(message):
    bot.reply_to(message, "📸 Барои таҳрири профил (ивази расм ва ном) ба @admin нависед.")

@bot.message_handler(commands=['security'])
def security(message):
    bot.reply_to(message, "🔐 **Танзимоти амният**\n\n✅ Тасдиқи дузинагӣ: Фаъол\n🔑 Рамзи махфӣ: Танзим нашудааст.")

@bot.message_handler(commands=['top_up'])
def top_up(message):
    bot.reply_to(message, "💰 **Пур кардани баланс**\n\n1. Корти Миллӣ (Душанбе Сити/Алиф)\n2. Криптовалюта (USDT)\n\nБарои пардохт ба @saidjun нависед.")

@bot.message_handler(commands=['make_site'])
def make_site(message):
    bot.reply_to(message, "🌐 **Конструктори сайтҳо**\n\nШумо метавонед сайти шахсии худро фармоиш диҳед. Нарх аз 100 TJS сар мешавад.")

@bot.message_handler(commands=['it_expert'])
def it_expert(message):
    bot.reply_to(message, "👨‍💻 **IT Expert AI**\n\nМан тайёрам ба саволҳои Python, HTML, CSS ва дигар забонҳо ҷавоб диҳам. Саволатонро нависед!")

@bot.message_handler(commands=['wallet'])
def wallet(message):
    bot.reply_to(message, "💳 **Ҳамёни ман**\n\nТаърихи амалиётҳо холӣ аст.")

@bot.message_handler(commands=['support'])
def support(message):
    bot.reply_to(message, "🎧 **Маркази дастгирӣ**\n\nСаволе доред? Нависед: @saidjun")

@bot.message_handler(commands=['help'])
def help_cmd(message):
    bot.reply_to(message, "❓ **Ёрӣ**\n\nБарои истифодаи бот аз тугмаҳои меню истифода баред ё мустақим ба AI савол диҳед.")

# --- ҶАВОБИ AI БА САВОЛҲОИ ОЗОД ---
@bot.message_handler(func=lambda message: True)
def ai_response(message):
    try:
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, "❌ Бубахшед, мағзи AI ҳоло банд аст.")

# --- БА КОР АНДОХТАН ---
def run_bot():
    bot.infinity_polling()

if __name__ == '__main__':
    threading.Thread(target=run_bot).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
