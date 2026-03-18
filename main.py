import os
import threading
import telebot
import google.generativeai as genai
from flask import Flask, render_template # Ин сатр хеле муҳим аст!

# Танзимоти калидҳо
TOKEN = os.environ.get('TELEGRAM_TOKEN')
API_KEY = os.environ.get('GEMINI_API_KEY')

bot = telebot.TeleBot(TOKEN)
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro')

app = Flask(__name__)

# Роҳи сайт
@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        return f"Хатогӣ дар ёфтани файл: {str(e)}"

# --- Ҷавоб ба тугмаҳои меню ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "📱 Хуш омадед ба Super-App!")

@bot.message_handler(commands=['profile'])
def profile(message):
    bot.reply_to(message, f"👤 Профили шумо\n🆔 ID: {message.from_user.id}")

@bot.message_handler(commands=['wallet'])
def wallet(message):
    bot.reply_to(message, "💳 Ҳамёни шумо холӣ аст.")

# Ҷавоби Gemini AI
@bot.message_handler(func=lambda message: True)
def ai_chat(message):
    response = model.generate_content(message.text)
    bot.reply_to(message, response.text)

def run_bot():
    bot.infinity_polling()

if __name__ == '__main__':
    # Сар додани бот дар замина
    threading.Thread(target=run_bot).start()
    # Сар додани сайт
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
