import os
import threading
import telebot
import google.generativeai as genai
from flask import Flask, render_template

# Танзимоти калидҳо аз Render Environment
TOKEN = os.environ.get('TELEGRAM_TOKEN')
API_KEY = os.environ.get('GEMINI_API_KEY')

bot = telebot.TeleBot(TOKEN)
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro')

app = Flask(__name__)

# --- WEB SITE ---
@app.route('/')
def index():
    return render_template('index.html')

# --- TELEGRAM BOT HANDLERS ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "📱 Хуш омадед ба Super-App! Ҳамаи тугмаҳо фаъоланд.")

@bot.message_handler(commands=['profile'])
def profile(message):
    bot.reply_to(message, f"👤 Кабинети шахсӣ\n🆔 ID: {message.from_user.id}\n💰 Баланс: 0.00 TJS")

@bot.message_handler(commands=['top_up'])
def top_up(message):
    bot.reply_to(message, "💰 Пур кардани баланс: Усули пардохтро интихоб кунед.")

@bot.message_handler(commands=['wallet'])
def wallet(message):
    bot.reply_to(message, "💳 Ҳамёни криптои шумо ҳоло пайваст нест.")

@bot.message_handler(commands=['it_expert'])
def it_expert(message):
    bot.reply_to(message, "👨‍💻 IT Expert AI омода аст. Саволи худро нависед.")

@bot.message_handler(commands=['support'])
def support(message):
    bot.reply_to(message, "🎧 Алоқа бо Админ: @saidjun")

# AI Response for other messages
@bot.message_handler(func=lambda message: True)
def ai_chat(message):
    try:
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except:
        bot.reply_to(message, "Бубахшед, хатогӣ дар AI.")

def run_bot():
    bot.infinity_polling()

if __name__ == '__main__':
    threading.Thread(target=run_bot).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
