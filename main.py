import os
import threading
import telebot
import google.generativeai as genai
from flask import Flask, render_template

# 1. Танзимоти калидҳо (Аз Render)
TOKEN = os.environ.get('TELEGRAM_TOKEN')
API_KEY = os.environ.get('GEMINI_API_KEY')

bot = telebot.TeleBot(TOKEN)
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro')

app = Flask(__name__)

# --- ҚИСМИ САЙТ (WEB) ---
@app.route('/')
def index():
    try:
        return render_template('index.html')
    except:
        return "Файли HTML ёфт нашуд. Боварӣ ҳосил кунед, ки templates/index.html ҳаст."

# --- ҲЕНДЛЕРҲОИ МЕНЮИ ТЕЛЕГРАМ ---

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "📱 Саҳифаи асосии Super-App ва Меню фаъол шуд!")

@bot.message_handler(commands=['profile'])
def profile(message):
    bot.reply_to(message, f"👤 **Кабинети шахсӣ**\n🆔 ID: {message.from_user.id}\n💰 Баланс: 0.00 TJS\n🌟 Статус: Корбар")

@bot.message_handler(commands=['edit_profile'])
def edit_profile(message):
    bot.reply_to(message, "📸 Барои иваз кардани расм ва маълумот ба @admin нависед.")

@bot.message_handler(commands=['security'])
def security(message):
    bot.reply_to(message, "🔐 Танзимоти амният:\nРамзи махфӣ ҳоло фаъол нест.")

@bot.message_handler(commands=['top_up'])
def top_up(message):
    bot.reply_to(message, "💰 Пур кардани баланс:\nЛутфан усули пардохтро интихоб кунед (Корти миллӣ/Крипто).")

@bot.message_handler(commands=['make_site'])
def make_site(message):
    bot.reply_to(message, "🌐 Конструктори сайтҳо:\nШумо метавонед сайти худро дар инҷо фармоиш диҳед.")

@bot.message_handler(commands=['it_expert'])
def it_expert(message):
    bot.reply_to(message, "👨‍💻 IT Expert AI:\nМан тайёрам ба ҳамаи саволҳои барномасозии шумо ҷавоб диҳам.")

@bot.message_handler(commands=['wallet'])
def wallet(message):
    bot.reply_to(message, "💳 Ҳамёни крипто ва таърихи пулҳо:\nҲоло ягон амалиёт иҷро нашудааст.")

@bot.message_handler(commands=['support'])
def support(message):
    bot.reply_to(message, "🎧 Алоқаи мустақим бо Админ: @saidjun")

@bot.message_handler(commands=['help'])
def help_cmd(message):
    bot.reply_to(message, "❓ Дастурамал:\nҲамаи тугмаҳо дар меню дастрасанд. Барои саволи озод танҳо нависед!")

# --- ҶАВОБИ GEMINI AI БАРОИ САВОЛҲОИ ОЗОД ---
@bot.message_handler(func=lambda message: True)
def ai_response(message):
    try:
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, "❌ Хатогӣ дар мағзи AI. Кӯшиш кунед дертар.")

# --- БА КОР АНДОХТАН ---
def run_bot():
    bot.infinity_polling()

if __name__ == '__main__':
    # Сар додани бот дар "поток"-и алоҳида
    threading.Thread(target=run_bot).start()
    # Сар додани сайт (Flask)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
