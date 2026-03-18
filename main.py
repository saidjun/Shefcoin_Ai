import os
import threading
import telebot
import google.generativeai as genai
from flask import Flask, render_template

# 1. Танзимоти калидҳо (Аз Render хонда мешаванд)
TOKEN = os.environ.get('TELEGRAM_TOKEN')
API_KEY = os.environ.get('GEMINI_API_KEY')

bot = telebot.TeleBot(TOKEN)
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro')

app = Flask(__name__)

# --- ҚИСМИ САЙТ (WEB INTERFACE) ---
@app.route('/')
def index():
    return render_template('index.html')

# --- ҚИСМИ ТЕЛЕГРАМ (BOT COMMANDS) ---

@bot.message_handler(commands=['start'])
def send_start(message):
    bot.reply_to(message, "📱 Хуш омадед ба Саҳифаи асосии Super-App ва Меню!\nМан омодаи хидматам.")

@bot.message_handler(commands=['profile'])
def send_profile(message):
    user = message.from_user
    text = (f"👤 **Кабинети шахсӣ**\n\n"
            f"🆔 ID: `{user.id}`\n"
            f"👤 Ном: {user.first_name}\n"
            f"💰 Баланс: 0.00 TJS\n"
            f"🌟 Статус: Корбар")
    bot.reply_to(message, text, parse_mode="Markdown")

@bot.message_handler(commands=['wallet'])
def send_wallet(message):
    bot.reply_to(message, "💳 **Ҳамёни крипто:**\n\nҲоло ягон ҳамён пайваст нест. Барои танзимот ба /support нависед.", parse_mode="Markdown")

@bot.message_handler(commands=['top_up'])
def send_topup(message):
    bot.reply_to(message, "💰 **Пур кардани баланс:**\n\nЛутфан усули пардохтро интихоб кунед:\n1. Корти Миллӣ\n2. Крипто (USDT/BTC)", parse_mode="Markdown")

@bot.message_handler(commands=['it_expert'])
def send_it(message):
    bot.reply_to(message, "👨‍💻 **IT Expert AI:**\n\nМан тайёрам ба саволҳои барномасозӣ ва техникии шумо ҷавоб диҳам. Танҳо саволро нависед!")

@bot.message_handler(commands=['support'])
def send_support(message):
    bot.reply_to(message, "🎧 **Маркази дастгирӣ:**\n\nАлоқаи мустақим бо Админ: @saidjun")

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message, "❓ **Ёрӣ:**\n\nТугмаҳоро аз меню пахш кунед ё ба ман мустақим савол диҳед, то AI ҷавоб диҳад.")

# Ҷавоби умумӣ бо AI Gemini
@bot.message_handler(func=lambda message: True)
def get_ai_response(message):
    try:
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except:
        bot.reply_to(message, "❌ Хатогӣ дар пайвастшавӣ бо AI. Лутфан қайта кӯшиш кунед.")

# --- БА КОР АНДОХТАНИ СИСТЕМА ---

def run_bot():
    bot.infinity_polling()

if __name__ == '__main__':
    # Ботро дар замина (background) сар медиҳем
    threading.Thread(target=run_bot).start()
    
    # Сайтро дар порте, ки Render медиҳад, сар медиҳем
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)



from flask import Flask, render_template
import os

app = Flask(__name__)

@app.route('/')
def index():
    # Ин сатр файли index.html-ро меҷӯяд
    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
